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
    <?php print theme(links, $primary_links); ?>
	<div id="content">
	<?php if ($title != ""): ?>
          <h2 class="content-title"><?php print $title ?></h2>
        <?php endif; ?>
        <?php if ($tabs != ""): ?>
          <?php print $tabs ?>
        <?php endif; ?>
       
        <?php if ($mission != ""): ?>
          <p id="mission"><?php print $mission ?></p>
        <?php endif; ?>
       
        <?php if ($help != ""): ?>
          <p id="help"><?php print $help ?></p>
        <?php endif; ?>
       
        <?php if ($messages != ""): ?>
          <div id="message"><?php print $messages ?></div>
        <?php endif; ?>

        <!-- start main content -->
        <?php print($content) ?>
        <!-- end main content -->
	
	</div>
	</body>

</html>
