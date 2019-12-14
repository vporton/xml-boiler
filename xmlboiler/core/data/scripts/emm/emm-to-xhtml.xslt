<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:basic="http://portonvictor.org/ns/EMM/basic"
                xmlns:text="http://portonvictor.org/ns/EMM/text"
                xmlns:access="http://portonvictor.org/ns/EMM/access"
                xmlns:handler="http://portonvictor.org/ns/EMM/handlers"
                xmlns:xforms="http://portonvictor.org/ns/EMM/xforms"
                xmlns:struct="http://portonvictor.org/ns/EMM/struct"
                xmlns:sections="http://portonvictor.org/ns/EMM/sections"
                xmlns:caption="http://portonvictor.org/ns/EMM/caption"
                xmlns:table="http://portonvictor.org/ns/EMM/table"
                xmlns:list="http://portonvictor.org/ns/EMM/list"
                xmlns:media="http://portonvictor.org/ns/EMM/media"
                xmlns:events="http://portonvictor.org/ns/EMM/events"
                xmlns:script="http://portonvictor.org/ns/EMM/script"
                xmlns:html="https://www.w3.org/2002/06/xhtml2">

    <xml:template match="basic:*|text:*|access:*|handler:*|xforms:*|struct:*|sections:*|caption:*|table:*|list:*|media:*|events:*|script:*">
        <xslt:element name="local-name" namespace="https://www.w3.org/2002/06/xhtml2">
            <xsl:apply-templates select="node()|@*"/>
        </xslt:element>
    </xml:template>
    
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
