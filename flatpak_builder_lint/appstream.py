import os
import subprocess
from typing import Optional

from lxml import etree

# for mypy
Element = etree._Element
ElementTree = etree._ElementTree


def validate(path: str) -> dict:
    if not os.path.isfile(path):
        raise FileNotFoundError("AppStream file not found")
    cmd = subprocess.run(
        ["appstream-util", "validate", "--nonet", path],
        capture_output=True,
    )

    ret = {
        "stdout": cmd.stdout.decode("utf-8"),
        "stderr": cmd.stderr.decode("utf-8"),
        "returncode": cmd.returncode,
    }

    return ret


def parse_xml(path: str) -> ElementTree:

    return etree.parse(path)


def components(path: str) -> list:

    components = parse_xml(path).xpath("/components/component")
    return list(components)


def is_developer_name_present(path: str) -> bool:
    developer = components(path)[0].xpath("developer_name")

    return bool(developer)


def is_project_license_present(path: str) -> bool:
    plicense = components(path)[0].xpath("project_license")

    return bool(plicense)


def component_type(path: str) -> str:

    return str(components(path)[0].attrib.get("type"))


def is_console(path: str) -> bool:
    if component_type(path) == "console-application":
        return True
    return False


def name(path: str) -> Optional[str]:
    for name in parse_xml(path).findall("component/name"):
        if not name.attrib.get(r"{http://www.w3.org/XML/1998/namespace}lang"):
            return str(name.text)
    return None


def summary(path: str) -> Optional[str]:
    for summary in parse_xml(path).findall("component/summary"):
        if not summary.attrib.get(r"{http://www.w3.org/XML/1998/namespace}lang"):
            return str(summary.text)
    return None


def check_caption(path: str) -> bool:
    exp = "//screenshot[not(caption/text()) or not(caption)]"

    return not any(e is not None for e in parse_xml(path).xpath(exp))
