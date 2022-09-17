from xmltodict import parse

from bd_bagarre.feed import generate_feed

expected = """<feed xmlns="http://www.w3.org/2005/Atom" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:pse="http://vaemendis.net/opds/ns" xmlns:opds="http://opds-spec.org/2010/catalog" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" xml:lang="en">
<id>d39dbb9cea3c4e059d2974b3165de55e-opdsRoot</id>
<title>BD Bagarre catalog</title>
<updated>2022-09-11T15:43:14+00:00</updated>
<icon>/theme/favicon.ico</icon>
<author>
<name>BD Bagarre server</name>
<uri>https://github.com/aubustou/bd_bagarre</uri>
</author>
<link type="application/atom+xml; profile=opds-catalog; kind=navigation" rel="self" href="/opds-comics/"/>
<link type="application/atom+xml; profile=opds-catalog; kind=navigation" rel="start" href="/opds-comics/"/>
<link type="application/opensearchdescription+xml" rel="search" href="/opds-comics/search"/>
<entry>
<title>All comics</title>
<id>allContentFlat</id>
<updated>2022-09-11T15:43:14+00:00</updated>
<content type="html">All comics presented as a list.</content>
<link type="application/atom+xml; profile=opds-catalog; kind=acquisition" rel="subsection" href="/opds-comics/all"/>
</entry>
<entry>
<title>Folders</title>
<id>allContentFolder</id>
<updated>2022-09-11T15:43:14+00:00</updated>
<content type="html">All comics grouped by folder.</content>
<link type="application/atom+xml; profile=opds-catalog; kind=navigation" rel="subsection" href="/opds-comics/all?groupByFolder=true"/>
</entry>
<entry>
<title>Latest comics</title>
<id>latestContent</id>
<updated>2022-09-11T15:43:14+00:00</updated>
<content type="html">Latest comics added to the collection</content>
<link type="application/atom+xml; profile=opds-catalog; kind=acquisition" rel="subsection" href="/opds-comics/?latest=true"/>
</entry>
</feed>
"""


def test_expected():
    generated = generate_feed()

    assert parse(generated) == parse(expected)
