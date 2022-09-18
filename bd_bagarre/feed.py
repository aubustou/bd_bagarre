from datetime import datetime
from typing import Any, TypedDict

import lxml.etree as etree
from feedgenerator import Atom1Feed as BaseAtom1Feed, get_tag_uri, rfc3339_date

from fastapi import APIRouter, Request, Response

router = APIRouter()


class Atom1Feed(BaseAtom1Feed):
    def add_root_elements(self, handler):
        handler.addQuickElement("title", self.feed["title"])

        handler.addQuickElement(
            "link",
            "",
            {
                "rel": "self",
                "type": "application/atom+xml; profile=opds-catalog; kind=navigation",
                "href": self.feed["self_link"],
            },
        )
        handler.addQuickElement(
            "link",
            "",
            {
                "rel": "start",
                "type": "application/atom+xml; profile=opds-catalog; kind=navigation",
                "href": self.feed["link"],
            },
        )
        if opensearch_description := self.feed.get("opensearch_description"):
            handler.addQuickElement(
                "link",
                "",
                {
                    "rel": "search",
                    "type": "application/opensearchdescription+xml",
                    "href": opensearch_description,
                },
            )

        handler.addQuickElement("id", self.feed["id"])
        handler.addQuickElement("updated", rfc3339_date(self.latest_post_date()))
        if self.feed["author_name"] is not None:
            handler.startElement("author", {})
            handler.addQuickElement("name", self.feed["author_name"])
            if self.feed["author_email"] is not None:
                handler.addQuickElement("email", self.feed["author_email"])
            if self.feed["author_link"] is not None:
                handler.addQuickElement("uri", self.feed["author_link"])
            handler.endElement("author")

        # try to use description or subtitle if provided, subtitle has
        # precedence above description
        if self.feed["subtitle"]:
            handler.addQuickElement("subtitle", self.feed["subtitle"])
        elif self.feed["description"]:
            handler.addQuickElement("subtitle", self.feed["description"])

        for cat in self.feed["categories"]:
            handler.addQuickElement("category", "", {"term": cat})

        if self.feed["feed_copyright"] is not None:
            handler.addQuickElement("rights", self.feed["feed_copyright"])

        if icon := self.feed.get("icon"):
            handler.addQuickElement("icon", icon)

    def root_attributes(self) -> dict[str, Any] | dict[str, str]:
        attributes = super().root_attributes()

        for name in [
            "xmlns_media",
            "xmlns_atom",
            "xmlns_dc",
            "xmlns_content",
            "xmlns_itunes",
            "xmlns_dcterms",
            "xmlns_pse",
            "xmlns_opds",
            "xmlns_opensearch",
        ]:
            if attribute := self.feed.get(name):
                attributes[name.replace("_", ":")] = attribute

        return attributes

    def add_item_elements(self, handler, item):
        handler.addQuickElement("title", item["title"])

        updateddate = datetime.now()
        if item["pubdate"] is not None:
            handler.addQuickElement("published", rfc3339_date(item["pubdate"]))
            updateddate = item["pubdate"]
        if item["updateddate"] is not None:
            updateddate = item["updateddate"]
        handler.addQuickElement("updated", rfc3339_date(updateddate))

        # Author information.
        if item["author_name"] is not None:
            handler.startElement("author", {})
            handler.addQuickElement("name", item["author_name"])
            if item["author_email"] is not None:
                handler.addQuickElement("email", item["author_email"])
            if item["author_link"] is not None:
                handler.addQuickElement("uri", item["author_link"])
            handler.endElement("author")

        # Unique ID.
        if item["unique_id"] is not None:
            unique_id = item["unique_id"]
        else:
            unique_id = get_tag_uri(item["link"], item["pubdate"])
        handler.addQuickElement("id", unique_id)

        # Summary.
        if item["description"] is not None:
            handler.addQuickElement("summary", item["description"], {"type": "html"})

        # Full content.
        if item["content"] is not None:
            handler.addQuickElement("content", item["content"], {"type": "html"})

        # Enclosure.
        if item["enclosure"] is not None:
            handler.addQuickElement(
                "link",
                "",
                {
                    "rel": "enclosure",
                    "href": item["enclosure"].url,
                    "length": item["enclosure"].length,
                    "type": item["enclosure"].mime_type,
                },
            )

        # Categories.
        for cat in item["categories"]:
            handler.addQuickElement("category", "", {"term": cat})

        # Rights.
        if item["item_copyright"] is not None:
            handler.addQuickElement("rights", item["item_copyright"])

        if (link_type := item.get("link_type")) and (
            link_rel := item.get("link_rel", "alternate")
        ):
            handler.addQuickElement(
                "link", "", {"rel": link_rel, "type": link_type, "href": item["link"]}
            )


feed_guid = "d39dbb9cea3c4e059d2974b3165de55e-{page}"
common_metadata = {
    "title": "BD Bagarre catalog",
    "description": None,
    "link": "/opds-comics/",
    "author_name": "BD Bagarre server",
    "author_link": "https://github.com/aubustou/bd_bagarre",
    "icon": "/theme/favicon.ico",
    "xmlns_dcterms": "http://purl.org/dc/terms/",
    "xmlns_pse": "http://vaemendis.net/opds/ns",
    "xmlns_opds": "http://opds-spec.org/2010/catalog",
    "xmlns_opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}


def generate_page_feed(self_link: str, items: list[dict]) -> str:
    feed = Atom1Feed(
        **common_metadata,
        self_link=self_link,
        feed_guid=feed_guid.format(page=self_link),
    )
    for item in items:
        feed.add_item(item)
    return feed.writeString("utf-8")


def generate_root_feed():
    feed = Atom1Feed(
        **common_metadata,
        feed_guid=feed_guid.format(page="opdsRoot"),
        self_link="/opds-comics/",
        opensearch_description="/opds-comics/search",
        language="en",
    )

    for id_, title, link, content, link_type, link_rel in [
        (
            "allContentFlat",
            "All comics",
            "/opds-comics/all",
            "All comics presented as a list.",
            "application/atom+xml; profile=opds-catalog; kind=acquisition",
            "subsection",
        ),
        (
            "allContentFolder",
            "Folders",
            "/opds-comics/folders",
            "All comics grouped by folder.",
            "application/atom+xml; profile=opds-catalog; kind=navigation",
            "subsection",
        ),
        (
            "latestContent",
            "Latest comics",
            "/opds-comics/latest",
            "Latest comics added to the collection",
            "application/atom+xml; profile=opds-catalog; kind=acquisition",
            "subsection",
        ),
    ]:
        feed.add_item(
            title=title,
            link=link,
            content=content,
            description=None,
            unique_id=id_,
            link_rel=link_rel,
            link_type=link_type,
        )
    return feed.writeString("utf-8")


def pretty_print_xml(xml: str) -> str:
    root = etree.fromstring(xml.encode())
    xml_string: str = etree.tostring(root, pretty_print=True).decode("utf-8")
    print(xml_string)

    return xml_string


def forge_response(xml: str) -> Response:
    return Response(
        content=xml.encode(),
        media_type="text/xml;charset=utf-8",
    )


@router.get("/opds-comics/")
async def opds_root() -> Response:
    return forge_response(generate_root_feed())


@router.get("/opds-comics/all")
async def opds_all(request: Request) -> Response:
    items = []
    return forge_response(generate_page_feed(request.url.path, items))


@router.get("/opds-comics/folders")
async def opds_folders(request: Request) -> Response:
    items = []
    return forge_response(generate_page_feed(request.url.path, items))


@router.get("/opds-comics/latest")
async def opds_latest(request: Request) -> Response:
    items = []
    return forge_response(generate_page_feed(request.url.path, items))

class BookFeed(TypedDict):
    title: str
    link: str
    content: str
    description: str
    id: str
    link_rel: str
    link_type: str
    category: str
    language: str

@router.get("/opds-comics/random")
async def opds_random(request: Request) -> Response:
    items = []
    return forge_response(generate_page_feed(request.url.path, items))


if __name__ == "__main__":
    pretty_print_xml(generate_root_feed())
