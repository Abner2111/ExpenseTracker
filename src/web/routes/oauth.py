"""Renew the Google OAuth token from the browser.

email_parser.py and sheets_manager.py both load src/token.pickle and, when it's
missing or the refresh token is dead, fall back to InstalledAppFlow.run_local_server()
- which opens a local port and browser *on the machine running the process*. That
works for a laptop, not a headless container on a remote server: nothing on that
machine can reach "localhost" inside the container.

This module does the equivalent flow the other way around: it builds a Google
consent URL, sends the operator's own browser to it, and on the redirect back
exchanges the code for credentials and writes token.pickle itself - no local
port/browser needed on the server at all.

Requires a separate OAuth client of type "Web application" (not the "Desktop"
one credentials.json already has) with this exact redirect URI registered in
Google Cloud Console, downloaded as src/web_credentials.json. Needs HTTPS
because Google won't redirect to a plain-HTTP non-localhost address.
"""

import os
import pickle

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from web.templating import templates

router = APIRouter()

_SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_WEB_CREDENTIALS_PATH = os.path.join(_SRC_DIR, "web_credentials.json")

# Single-operator admin tool behind HTTP Basic Auth already - a process-wide
# slot for the pending CSRF state is enough, no need for real session storage.
_pending_state = {"value": None}


def _redirect_uri(request: Request) -> str:
    return f"{request.url.scheme}://{request.url.netloc}/oauth/callback"


def _build_flow(request: Request, state: str | None = None):
    from config_manager import config_manager
    from google_auth_oauthlib.flow import Flow

    return Flow.from_client_secrets_file(
        _WEB_CREDENTIALS_PATH,
        scopes=config_manager.get_google_scopes(),
        state=state,
        redirect_uri=_redirect_uri(request),
    )


@router.get("/oauth/start")
def oauth_start(request: Request):
    if not os.path.exists(_WEB_CREDENTIALS_PATH):
        return RedirectResponse(
            url="/status?oauth_error=web_credentials.json+not+found+on+the+server", status_code=303
        )

    flow = _build_flow(request)
    # prompt=consent forces Google to reissue a refresh_token every time - without
    # it, a second authorization for the same account can come back access-token-only.
    # device_id/device_name are required by Google for redirect URIs on a private
    # IP (RFC 1918, e.g. 192.168.x.x) - arbitrary values, just need to be present.
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
        device_id="expensetracker-web-oauth",
        device_name="ExpenseTracker Web UI",
    )
    _pending_state["value"] = state
    return RedirectResponse(url=authorization_url, status_code=303)


@router.get("/oauth/callback")
def oauth_callback(request: Request):
    error = request.query_params.get("error")
    if error:
        return RedirectResponse(url=f"/status?oauth_error={error}", status_code=303)

    state = request.query_params.get("state")
    if not state or state != _pending_state["value"]:
        return RedirectResponse(url="/status?oauth_error=state+mismatch,+try+again", status_code=303)
    _pending_state["value"] = None

    try:
        from config_manager import config_manager

        flow = _build_flow(request, state=state)
        flow.fetch_token(authorization_response=str(request.url))

        token_path = config_manager.get_token_path()
        with open(token_path, "wb") as f:
            pickle.dump(flow.credentials, f)
    except Exception as e:
        return RedirectResponse(url=f"/status?oauth_error={e}", status_code=303)

    return RedirectResponse(url="/status?oauth_renewed=true", status_code=303)
