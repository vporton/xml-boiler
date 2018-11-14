<!--
Borrowed from https://stackoverflow.com/a/11496690/856090
Caveats: This solution does not implement the attributes: xpointer, accept and accept-language.
fn:unparsed-text-available() does not work in Saxon HE 9.1.0.8J
-->
<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xi="http://www.w3.org/2001/XInclude"
  xmlns:fn="http://www.w3.org/2005/xpath-functions"
  exclude-result-prefixes='xsl xi fn'>

<!--xsl:output method="xml" indent="no"/-->

<xsl:template match="@*|node()">
 <xsl:copy>
  <xsl:apply-templates select="@*|node()"/>
 </xsl:copy>
</xsl:template>

<!--xsl:template match="xi:include[@href][@parse='xml' or not(@parse)][fn:unparsed-text-available(@href)]"-->
<xsl:template match="xi:include[@href][@parse='xml' or not(@parse)]">
 <xsl:apply-templates select="fn:document(@href)" />
</xsl:template>

<!--xsl:template match="xi:include[@href][@parse='text'][fn:unparsed-text-available(@href)]"-->
<xsl:template match="xi:include[@href][@parse='text']">
 <xsl:value-of select="fn:unparsed-text(@href,@encoding)" />
</xsl:template>

<!--
<xsl:template match="xi:include[@href][@parse=('text','xml') or not(@parse)][not(fn:unparsed-text-available(@href))][xi:fallback]">
 <xsl:apply-templates select="xi:fallback/text()" />
</xsl:template>
-->

<xsl:template match="xi:include" />

</xsl:stylesheet>
