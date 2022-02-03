from re import compile

from fastapi import APIRouter, HTTPException, Request
from ormar import NoMatch

from src.impl.utils import Noofile
from src.impl.database import Key, Project, User
from src.impl.utils import Authenticator

from .models import KeyRequest, KeyResponse, KeysResponse, ProjectResponse, UserRequest

router = APIRouter(prefix="/users")


USERNAME = compile(r"^[a-zA-Z0-9_]{3,32}$")


@router.get("/{username}", response_model=User)
@Authenticator.require()
async def get_user(request: Request, username: str) -> User:
    """
    Get an API user.

    This is an admin-only endpoint.
    """

    try:
        user = await User.objects.first(username=username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/", response_model=User)
@Authenticator.require()
async def create_user(request: Request, user_req: UserRequest) -> User:
    """
    Create an API user.

    This is an admin-only endpoint.
    """

    if not USERNAME.match(user_req.username):
        raise HTTPException(status_code=400, detail="Invalid username")

    user = User(**user_req.dict())
    await user.save()

    return user


@router.patch("/{username}", response_model=User)
@Authenticator.require()
async def update_user(request: Request, username: int, user_req: UserRequest) -> User:
    """
    Update an API user.

    This is an admin-only endpoint.
    """

    try:
        user = await User.objects.first(username=username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="User not found")

    return await user.update(**user_req.dict())


@router.delete("/{username}")
@Authenticator.require()
async def delete_user(request: Request, username: int) -> None:
    """
    Delete an API user.

    This is an admin-only endpoint.
    """

    try:
        user = await User.objects.first(username=username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="User not found")

    await user.delete()


@router.post("/{username}/keys", response_model=KeyResponse)
@Authenticator.require()
async def create_key(request: Request, username: int, key_req: KeyRequest) -> KeyResponse:
    """
    Create an API user key.

    This is an admin-only endpoint.
    """

    try:
        user = await User.objects.first(username=username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="User not found")

    key = Key(user=user, **key_req.dict())
    await key.save()

    return KeyResponse(
        key=key.dict(),  # type: ignore
        token=Authenticator.generate_jwt(user.username, key.project, key.id),
    )


@router.get("/{username}/keys", response_model=KeysResponse)
@Authenticator.require()
async def get_keys(request: Request, username: int) -> KeysResponse:
    """
    Get an API user's keys.

    This is an admin-only endpoint.
    """

    try:
        user = await User.objects.first(username=username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="User not found")

    return KeysResponse(keys=await Key.objects.all(user=user.username))


@router.get("/{username}/keys/{key_id}", response_model=KeyResponse)
@Authenticator.require()
async def get_key(request: Request, username: int, key_id: int) -> KeyResponse:
    """
    Get an API user's key.

    This is an admin-only endpoint.
    """

    try:
        user = await User.objects.first(username=username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        key = await Key.objects.first(id=key_id, user=user.username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="Key not found")

    return KeyResponse(key=key, token=Authenticator.generate_jwt(user.username, key.project, key.id))


@router.patch("/{username}/keys/{key_id}", response_model=KeyResponse)
@Authenticator.require()
async def update_key(request: Request, username: int, key_id: int, key_req: KeyRequest) -> KeyResponse:
    """
    Update an API user's key.

    This is an admin-only endpoint.
    """

    try:
        user = await User.objects.first(username=username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        key = await Key.objects.first(id=key_id, user=user.username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="Key not found")

    return KeyResponse(
        key=await key.update(**key_req.dict()),
        token=Authenticator.generate_jwt(user.username, key.project, key.id),
    )


@router.delete("/{username}/keys/{key_id}")
@Authenticator.require()
async def delete_key(request: Request, username: int, key_id: int) -> None:
    """
    Delete an API user's key.

    This is an admin-only endpoint.
    """

    try:
        user = await User.objects.first(username=username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        key = await Key.objects.first(id=key_id, user=user.username)
    except NoMatch:
        raise HTTPException(status_code=404, detail="Key not found")

    await key.delete()


@router.get("/{username}/projects/{project}", response_model=ProjectResponse)
async def get_project(username: str, project: str, version: str = None) -> ProjectResponse:
    """Get a project."""

    try:
        if version:
            db_project = await Project.objects.first(user=username, name=project, version=version)
        else:
            db_project = await Project.objects.filter().order_by(Project.id.desc()).first(user=username, name=project)  # type: ignore
    except NoMatch:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(name=project, username=username, spec=Noofile(**db_project.spec), version=db_project.version)


@router.post("/{username}/projects/{project}/{version}", response_model=ProjectResponse)
@Authenticator.require()
async def create_project(request: Request, username: str, project: str, version: str, spec: Noofile) -> ProjectResponse:
    """
    Create a project.

    This endpoint requires user authentication.
    """

    auth_user: str = request.state.username
    auth_project: str = request.state.project

    if auth_project != "*" and auth_project != project:
        raise HTTPException(status_code=403, detail="This key does not have access to push to this project")

    if auth_user != username:
        raise HTTPException(
            status_code=403, detail=f"User {auth_user} does not have permission to push to @{username}/{project}"
        )

    try:
        await Project.objects.first(user=username, name=project, version=version)

        raise HTTPException(status_code=409, detail=f"Project @{username}/{project}#{version} already exists")
    except NoMatch:
        pass

    await Project(user=username, name=project, version=version, spec=spec.dict()).save()

    return ProjectResponse(name=project, username=username, spec=spec, version=version)
