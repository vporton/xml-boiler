<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns:struct="http://portonvictor.org/ns/myxhtml/struct"
                version='1.0'
                exclude-result-prefixes="struct">

  <xsl:import href="copy.xslt"/>

  <xsl:output method="xml"/>

  <xsl:template match="struct:toc">
    <xsl:for-each select="//h:html/h:body">
      <xsl:call-template name="struct:toc"/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template name="struct:toc">
    <xsl:if test="struct:section">
      <ul class="ToC">
        <xsl:for-each select="struct:section">
          <li>
            <xsl:variable name="id">
              <xsl:choose>
                <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
                <xsl:otherwise><xsl:value-of select="generate-id()"/></xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <a href="#{$id}">
              <xsl:copy-of select="struct:title/@xml:lang"/>
              <xsl:apply-templates select="struct:title/node()"/>
            </a>
            <xsl:call-template name="struct:toc"/>
          </li>
        </xsl:for-each>
      </ul>
    </xsl:if>
  </xsl:template>

  <xsl:template match="struct:section">
    <xsl:variable name="count" select="count(ancestor::struct:section)" />
    <xsl:if test="$count>5">
      <xsl:message terminate="yes">Too deep header</xsl:message>
    </xsl:if>
    <xsl:element name="h{$count+2}">
      <xsl:attribute name="id">
        <xsl:choose>
          <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
          <xsl:otherwise><xsl:value-of select="generate-id()"/></xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:apply-templates select="struct:title[1]/node()" /><!-- TODO: simplfy -->
    </xsl:element>
    <xsl:apply-templates/>
  </xsl:template>

  <!--xsl:template match="@href[parent::h:a and starts-with(.,'#')]">
    <xsl:attribute name="href">
      <xsl:text>#</xsl:text>
      <xsl:value-of
    </xsl:attribute>
  </xsl:template-->

  <xsl:template match="struct:title" />

</xsl:stylesheet>
