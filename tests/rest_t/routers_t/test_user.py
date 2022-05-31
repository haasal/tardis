from tests.rest_t.routers_t.base_test_case_routers import TestCaseRouters
from tests.utilities.utilities import run_async

# TODO: decrease code repetition by extracting basic auth test into separate function


class TestLogin(TestCaseRouters):
    # Reminder: When defining `setUp`, `setUpClass`, `tearDown` and `tearDownClass`
    # in router tests the corresponding super().function() needs to be called as well.
    def test_login(self):
        # No body and headers
        self.clear_lru_cache()
        response = run_async(self.client.post, "/user/login")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json(),
            {
                "detail": [
                    {
                        "loc": ["body"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ]
            },
        )

        # Empty body
        self.clear_lru_cache()
        response = run_async(self.client.post, "/user/login", data="{}")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json(),
            {
                "detail": [
                    {
                        "loc": ["body", "user_name"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["body", "password"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                ]
            },
        )

        self.clear_lru_cache()
        response = run_async(self.client.post, "/user/login", json=self.test_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"msg": "Successfully logged in!"},
        )

        self.clear_lru_cache()
        self.config.Services.restapi.get_user.side_effect = lambda user_name: None
        response = run_async(self.client.post, "/user/login", json=self.test_user)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Incorrect username or password"})
        self.config.Services.restapi.get_user.side_effect = None

        self.clear_lru_cache()
        self.test_user["password"] = "wrong"
        response = run_async(self.client.post, "/user/login", json=self.test_user)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Incorrect username or password"})

    def test_logout(self):
        # Not logged in yet
        self.clear_lru_cache()
        response = run_async(self.client.delete, "/user/logout")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(), {"detail": "Missing cookie access_token_cookie"}
        )

        # correct login
        self.login()
        response = run_async(self.client.delete, "/user/logout")
        self.assertEqual(response.status_code, 200)

        # prevent second logout
        response = run_async(self.client.delete, "/user/logout")
        self.assertEqual(response.status_code, 401)

    def test_refresh(self):
        # Not logged in yet
        self.clear_lru_cache()
        response = run_async(self.client.post, "/user/refresh")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(), {"detail": "Missing cookie refresh_token_cookie"}
        )

        # correct login
        self.login()
        response = run_async(self.client.post, "/user/refresh")
        self.assertEqual(response.status_code, 200)

    def test_user_me(self):
        # Not logged in yet
        self.clear_lru_cache()
        response = run_async(self.client.get, "/user/me")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(), {"detail": "Missing cookie access_token_cookie"}
        )

        # should work
        self.login()
        response = run_async(self.client.get, "/user/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"user_name": "test", "scopes": ["resources:get"]}
        )
