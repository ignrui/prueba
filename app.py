"""
Flask REST API Microservice
Simple task management API with PostgreSQL database
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
from sqlalchemy import text
import os
from datetime import datetime

db = SQLAlchemy()


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
        }


def create_app(test_config=None):
    app = Flask(__name__)

    # Database configuration
    if test_config is not None:
        app.config.update(test_config)
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
            "DATABASE_URL", "postgresql://devops:devops123@db:5432/tasksdb"
        )
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    PrometheusMetrics(app)

    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            # Check database connectivity
            with app.app_context():
                db.session.execute(text("SELECT 1"))
            return (
                jsonify(
                    {
                        "status": "healthy",
                        "database": "connected",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                200,
            )
        except Exception as e:
            return (
                jsonify(
                    {
                        "status": "unhealthy",
                        "database": "disconnected",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                503,
            )

    @app.route("/ready", methods=["GET"])
    def readiness_check():
        """Readiness check endpoint"""
        return jsonify({"status": "ready"}), 200

    @app.route("/api/tasks", methods=["GET"])
    def get_tasks():
        """Get all tasks"""
        tasks = Task.query.all()
        return jsonify([task.to_dict() for task in tasks]), 200

    @app.route("/api/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        """Get a single task by ID"""
        task = Task.query.get_or_404(task_id)
        return jsonify(task.to_dict()), 200

    @app.route("/api/tasks", methods=["POST"])
    def create_task():
        """Create a new task"""
        data = request.get_json()

        if not data or "title" not in data:
            return jsonify({"error": "Title is required"}), 400

        task = Task(
            title=data["title"],
            description=data.get("description", ""),
            completed=data.get("completed", False),
        )

        db.session.add(task)
        db.session.commit()

        return jsonify(task.to_dict()), 201

    @app.route("/api/tasks/<int:task_id>", methods=["PUT"])
    def update_task(task_id):
        """Update an existing task"""
        task = Task.query.get_or_404(task_id)
        data = request.get_json()

        if "title" in data:
            task.title = data["title"]
        if "description" in data:
            task.description = data["description"]
        if "completed" in data:
            task.completed = data["completed"]

        db.session.commit()
        return jsonify(task.to_dict()), 200

    @app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        """Delete a task"""
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted successfully"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
