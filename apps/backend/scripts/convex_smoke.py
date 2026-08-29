"""Verify the deployed Convex event mutation and its idempotency guard."""

import os

from convex.values import CoercibleToConvexValue

from convex import ConvexClient


def main() -> None:
    convex_url = os.environ.get("CONVEX_URL")
    if not convex_url:
        raise SystemExit("CONVEX_URL is required for the Convex smoke test")

    delivery_id = "smoke-20260829-convex-ready"
    payload: dict[str, CoercibleToConvexValue] = {
        "deliveryId": delivery_id,
        "eventType": "push",
        "repositoryFullName": "DiogoFabricioAG/commit-content-creator",
        "branch": "main",
        "commitShas": ["smoke-20260829"],
    }

    client = ConvexClient(convex_url)
    first = client.mutation("githubEvents:record", payload)
    second = client.mutation("githubEvents:record", payload)
    saved = client.query("githubEvents:getByDeliveryId", {"deliveryId": delivery_id})

    if first["duplicate"] is not False:
        raise SystemExit("the first mutation call was unexpectedly deduplicated")
    if second["duplicate"] is not True:
        raise SystemExit("the second mutation call did not hit the idempotency guard")
    if saved is None or saved["status"] != "received":
        raise SystemExit("the event was not persisted with status=received")

    print("convex_smoke=passed; duplicate_guard=passed; persisted_status=received")


if __name__ == "__main__":
    main()
