<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="copy.xslt"/>

<xsl:output method="xml"/>

<xsl:template match="xi:include" xmlns:xi="http://www.w3.org/2001/XInclude">
  <xsl:for-each select="document(@href)">
    <xsl:apply-templates/>
  </xsl:for-each>
</xsl:template>

</xsl:stylesheet>
