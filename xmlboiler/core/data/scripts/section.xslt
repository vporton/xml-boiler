<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:h="http://www.w3.org/1999/xhtml"
                xmlns:sections="http://portonvictor.org/ns/EMM/sections"
                xmlns:toc="http://portonvictor.org/ns/EMM/toc"
                version='1.0'
                exclude-result-prefixes="sections">

  <xsl:import href="copy.xslt"/>

  <xsl:output method="xml"/>

  <xsl:template match="toc:toc">
    <xsl:for-each select="//h:html/h:body">
      <xsl:call-template name="toc:toc"/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template name="toc:toc">
    <xsl:if test="sections:section">
      <ul class="ToC">
        <xsl:for-each select="sections:section">
          <li>
            <xsl:variable name="id">
              <xsl:choose>
                <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
                <xsl:otherwise><xsl:value-of select="generate-id()"/></xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <a href="#{$id}">
              <xsl:copy-of select="sections:h/@xml:lang"/>
              <xsl:apply-templates select="sections:h/node()"/>
            </a>
            <xsl:call-template name="toc:toc"/>
          </li>
        </xsl:for-each>
      </ul>
    </xsl:if>
  </xsl:template>

  <xsl:template match="sections:section">
    <xsl:variable name="count" select="count(ancestor::sections:section)" />
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
      <xsl:apply-templates select="sections:h[1]/node()" />
    </xsl:element>
    <xsl:apply-templates/>
  </xsl:template>

  <!--xsl:template match="@href[parent::h:a and starts-with(.,'#')]">
    <xsl:attribute name="href">
      <xsl:text>#</xsl:text>
      <xsl:value-of
    </xsl:attribute>
  </xsl:template-->

  <xsl:template match="sections:h" />

</xsl:stylesheet>
