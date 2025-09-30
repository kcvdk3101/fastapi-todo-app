# URL Constants
auth = {
  "prefix": "/auth",
  "tags": ["Auth"],
  "urls": {
    "login": "/login"
  }
}

company = {
  "prefix": "/companies",
  "tags": ["Companies"],
  "urls": {
    "get_my_company": "/me",
    "get_company_by_id": "/{company_id}",
    "create_company": "",
    "update_company": "/{company_id}"
  }
}

user = {
  "prefix": "/users",
  "tags": ["Users"],
  "urls": {
    "get_me": "/me",
    "get_user_by_id": "/{user_id}",
    "create_user": "",
    "list_users": "",
    "update_user": "/{user_id}",
    "delete_user": "/{user_id}"
  }
}

todo = {
  "prefix": "/todos",
  "tags": ["Todos"],
  "urls": {
    "get_task_by_id": "/{task_id}",
    "create_task": "",
    "update_task": "/{task_id}",
    "delete_task": "/{task_id}",
    "list_tasks": ""
  }
}