# Projet_10, SoftDesk API

SoftDesk is a collaborative RESTful API designed for managing projects, issues, and comments with role-based permissions.

## Features

### Authentication

* JWT-based authentication using `djangorestframework-simplejwt`.
* All endpoints require a valid access token.

### Projects

* **List Projects**: Any authenticated user can view a list of all projects.
* **Create Project**: Any authenticated user can create a project and automatically becomes a contributor to it.
* **Retrieve Project**: Only contributors of a project can retrieve its details.
* **Update/Delete Project**: Only the project **author** can update or delete the project.

### Issues (Nested under Projects)

* **List Issues**: Only contributors of the parent project can view its issues.
* **Create Issue**: Only contributors can create an issue. The creator becomes the issue **author**.
* **Retrieve Issue**: Only contributors can retrieve issue details.
* **Update/Delete Issue**: Only the issue **author** can update or delete their issue.

### Comments (Nested under Issues)

* **List Comments**: Only contributors of the parent project can view comments.
* **Create Comment**: Only contributors can add a comment. The commenter becomes the comment **author**.
* **Update/Delete Comment**: Only the comment **author** can update or delete their comment.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/97jayv122/Projet_10.git
   cd Projet_10
   ```
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Apply migrations:

   ```bash
   python manage.py migrate
   ```
5. Run the development server:

   ```bash
   python manage.py runserver
   ```

## API Endpoints

Authentication:

* **Obtain Token**: `POST /api/token/`
* **Refresh Token**: `POST /api/token/refresh/`

Projects:

* `GET /api/projects/` : List all projects
* `POST /api/projects/` : Create a new project
* `GET /api/projects/{project_id}/` : Retrieve project details
* `PATCH /api/projects/{project_id}/` : Update project (author only)
* `DELETE /api/projects/{project_id}/` : Delete project (author only)

Issues:

* `GET /api/projects/{project_id}/issues/` : List issues for a project
* `POST /api/projects/{project_id}/issues/` : Create a new issue
* `GET /api/projects/{project_id}/issues/{issue_id}/` : Retrieve issue details
* `PATCH /api/projects/{project_id}/issues/{issue_id}/` : Update issue (author only)
* `DELETE /api/projects/{project_id}/issues/{issue_id}/` : Delete issue (author only)

Comments:

* `GET /api/projects/{project_id}/issues/{issue_id}/comments/` : List comments for an issue
* `POST /api/projects/{project_id}/issues/{issue_id}/comments/` : Create a new comment
* `GET /api/projects/{project_id}/issues/{issue_id}/comments/{comment_id}/` : Retrieve comment details
* `PATCH /api/projects/{project_id}/issues/{issue_id}/comments/{comment_id}/` : Update comment (author only)
* `DELETE /api/projects/{project_id}/issues/{issue_id}/comments/{comment_id}/` : Delete comment (author only)

Contributor Management:

* `GET /api/contributor/` : List projects the user contributes to
* `POST /api/contributor/` : Add oneself as a contributor to a project

## Testing

Run the full test suite with:

```bash
python manage.py test
```

All tests should pass, verifying correct permission and CRUD behavior.