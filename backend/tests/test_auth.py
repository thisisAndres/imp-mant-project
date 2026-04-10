"""
Tests for authentication, token security, role-based access control, and user CRUD.
Covers: app/api/v1/auth.py, app/api/v1/users.py, app/services/auth_service.py,
        app/core/security.py, app/core/dependencies.py, app/repositories/user_repo.py
"""

from tests.conftest import _test_sf, create_user_in_db


# ── Health ────────────────────────────────────────────────────────────────────

async def test_health_check(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ── Login ─────────────────────────────────────────────────────────────────────

async def test_login_success(client):
    await create_user_in_db("login@example.com", "ValidPass1!", "admin")
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "ValidPass1!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await create_user_in_db("login@example.com", "ValidPass1!", "admin")
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "WrongPass1!"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_email(client):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "AnyPass1!"},
    )
    assert resp.status_code == 401


async def test_login_inactive_user(client):
    from sqlalchemy import select
    from app.models.user import User

    await create_user_in_db("inactive@example.com", "ValidPass1!", "employee")

    async with _test_sf() as session:
        user = (
            await session.execute(
                select(User).where(User.email == "inactive@example.com")
            )
        ).scalar_one()
        user.is_active = False
        await session.commit()

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "ValidPass1!"},
    )
    assert resp.status_code == 401


# ── Refresh token ─────────────────────────────────────────────────────────────

async def test_refresh_token_success(client):
    await create_user_in_db("refresh@example.com", "ValidPass1!", "admin")
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "refresh@example.com", "password": "ValidPass1!"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_refresh_with_access_token_fails(client):
    """Submitting an access token to the refresh endpoint must be rejected."""
    await create_user_in_db("refresh@example.com", "ValidPass1!", "admin")
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "refresh@example.com", "password": "ValidPass1!"},
    )
    access_token = login_resp.json()["access_token"]

    resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": access_token}
    )
    assert resp.status_code == 401


async def test_refresh_with_invalid_token_fails(client):
    resp = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "not.a.valid.jwt"}
    )
    assert resp.status_code == 401


# ── Protected route access ────────────────────────────────────────────────────

async def test_protected_route_no_auth(client):
    """HTTPBearer returns 403 when no Authorization header is provided."""
    resp = await client.get("/api/v1/products/")
    assert resp.status_code == 403


async def test_protected_route_invalid_token(client):
    resp = await client.get(
        "/api/v1/products/",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert resp.status_code == 401


async def test_protected_route_valid_token(client, employee_token):
    resp = await client.get(
        "/api/v1/products/",
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 200


# ── Users CRUD (admin only) ───────────────────────────────────────────────────

async def test_list_users_as_admin(client, admin_token):
    resp = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_list_users_as_manager_forbidden(client, manager_token):
    resp = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert resp.status_code == 403


async def test_create_user_as_admin(client, admin_token):
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "password": "NewUser1!",
            "full_name": "New User",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@example.com"
    assert data["is_active"] is True


async def test_create_user_weak_password_rejected(client, admin_token):
    resp = await client.post(
        "/api/v1/users/",
        json={"email": "weak@example.com", "password": "weak", "full_name": "Weak User"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 422


async def test_create_user_as_employee_forbidden(client, employee_token):
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "password": "NewUser1!",
            "full_name": "New User",
        },
        headers={"Authorization": f"Bearer {employee_token}"},
    )
    assert resp.status_code == 403


async def test_get_user_by_id(client, admin_token):
    create_resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "getme@example.com",
            "password": "GetMe123!",
            "full_name": "Get Me",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    user_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == user_id


async def test_get_user_not_found(client, admin_token):
    resp = await client.get(
        "/api/v1/users/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 404


async def test_update_user_as_admin(client, admin_token):
    create_resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "updateme@example.com",
            "password": "Update123!",
            "full_name": "Update Me",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    user_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/users/{user_id}",
        json={"full_name": "Updated Name"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Updated Name"


async def test_deactivate_user_as_admin(client, admin_token):
    create_resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "deactivate@example.com",
            "password": "Deact123!",
            "full_name": "Deactivate Me",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    user_id = create_resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False
