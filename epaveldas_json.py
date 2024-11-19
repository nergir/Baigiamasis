import json
import os

import requests


def main(url: str) -> None:
    """Main."""
    r = requests.get(url)
    d = r.json()
    json.dump(d, open("epaveldas.json", "w"))  # noqa: SIM115
    print(json.dumps(d, indent=4))

    res = d.get("periodics")
    for k in res:
        print(k)
        for i in res[k]:
            print(i.get("number"), i.get("id"))
            if os.path.exists("json/" + i.get("id") + ".json"):  # noqa: PTH110
                continue
            resp = requests.get(
                "https://www.epaveldas.lt/vepis-api/internal/findById",
                params=dict(id=i.get("id")),
            )

            resp.ok and json.dump(resp.json(), open("json/" + i.get("id") + ".json", "w"))  # noqa: SIM115


if __name__ == "__main__":
    url = "https://www.epaveldas.lt/vepis-api/internal/findById?id=C1B0003883315"
    main(url)
