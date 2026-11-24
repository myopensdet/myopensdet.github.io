# Template from myOpenSDET: https://myopensdet.github.io/
"""A small GraphQL client for tests.

GraphQL sends every request to one address, as a POST with a JSON body:
    {"query": "...", "variables": {...}}
and the answer is JSON with "data", "errors", or both. Many servers answer 200
even when there are errors, so a test must always look at "errors".

    client = GraphQLClient("https://graphqlzero.almansi.me/api")
    post = client.data(QUERY, {"id": "1"})["post"]      # fails loudly on any error
    answer = client.execute(QUERY, {"id": "x"})         # the raw answer, to test errors
"""

import logging

import requests

log = logging.getLogger("graphql")


class GraphQLError(AssertionError):
    """The server answered with errors. The message lists each one, with its code and path."""

    def __init__(self, answer: "Answer"):
        self.answer = answer
        lines = [f"GraphQL answered {answer.status} with {len(answer.errors)} error(s):"]
        for error in answer.errors:
            code = error.get("extensions", {}).get("code", "no code")
            path = ".".join(str(p) for p in error.get("path", [])) or "-"
            lines.append(f"  [{code}] at {path}: {error.get('message')}")
        super().__init__("\n".join(lines))


class Answer:
    """One GraphQL answer: the HTTP status, plus the data and errors from the JSON body."""

    def __init__(self, response: requests.Response):
        self.status = response.status_code
        try:
            body = response.json()
        except ValueError:
            raise AssertionError(
                f"Not a GraphQL answer: {response.status_code} "
                f"{response.headers.get('Content-Type')} {response.text[:200]!r}"
            ) from None
        self.data = body.get("data")
        self.errors = body.get("errors") or []

    def codes(self) -> list[str]:
        """The error codes, like ['BAD_USER_INPUT']. Easier to assert on than messages."""
        return [e.get("extensions", {}).get("code", "") for e in self.errors]


class GraphQLClient:
    def __init__(self, url: str, timeout: float = 15, headers: dict | None = None):
        self.url = url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", **(headers or {})})

    def execute(self, query: str, variables: dict | None = None, operation: str | None = None):
        """Send one query or mutation. Returns the Answer, errors and all."""
        body = {"query": query}
        if variables is not None:
            body["variables"] = variables
        if operation is not None:
            body["operationName"] = operation
        response = self.session.post(self.url, json=body, timeout=self.timeout)
        answer = Answer(response)
        log.info(
            "POST %s %s -> %s, %d error(s), in %d ms",
            self.url,
            operation or query.split("{")[0].strip() or "query",
            answer.status,
            len(answer.errors),
            response.elapsed.total_seconds() * 1000,
        )
        return answer

    def data(self, query: str, variables: dict | None = None, operation: str | None = None):
        """Send it, and return "data". Fails on any error, even when the status is 200."""
        answer = self.execute(query, variables, operation)
        if answer.errors or answer.status != 200:
            raise GraphQLError(answer)
        return answer.data

    def close(self) -> None:
        self.session.close()
