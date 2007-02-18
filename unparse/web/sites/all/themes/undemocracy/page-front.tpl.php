<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="<?php print $language ?>" lang="<?php print $language ?>">
  <head>
    <title><?php print $head_title ?></title>
    <?php print $head ?>
    <?php print $styles ?>
    <?php print $scripts ?>
    </head>

 <body>

	<h1 id="logo"><a href="<?php print url() ?>"><span class="un">UN</span>DEMOCRACY<span class="com">.COM</span></a></h1>
	<div id="map"></div>
	<div id="left" class="mapcol"></div>
	<div id="right" class="mapcol"></div>
	<div id="intro"><?php print variable_get('intro_text', 'intro text here'); ?></div>
	<div id="blocks">
	<?php print $front; ?>
	</div>
    </body>

</html>
