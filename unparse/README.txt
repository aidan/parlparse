UN project
==========

Please document here files and directories which you make.

scraper - Julian's scraper and parser
bin - Scripts and executables
web - Drupal-based website code
web2 - Python-based website code

phplib - Python modules
perllib - Perl modules

Apache configuration
====================

Needs some fancy mod-rewrite rules. Do something like this:

# Staging site
<VirtualHost *:80>
    ServerName staging.undemocracy.com

    ServerAdmin info@undemocracy.com
    DocumentRoot /data/vhost/staging.undemocracy.com/docs

    RewriteEngine on
    #RewriteLog /var/log/apache/rewrite.log
    #RewriteLogLevel 3
    RewriteCond %{REQUEST_URI} !^/.*.css
    RewriteCond %{REQUEST_URI} !^/.*.js
    RewriteCond %{REQUEST_URI} !^/.*.png
    RewriteCond %{REQUEST_URI} !^/images/.*
    RewriteRule ^/(.*)$ /trunk.py/$1 [PT,L,QSA]

    <Directory "/data/vhost/staging.undemocracy.com/docs/">
        AllowOverride All
        Options FollowSymLinks
        Order allow,deny
        Allow from all
        Options +ExecCGI
        AddHandler cgi-script .cgi .py
    </Directory>

    Alias /pdf/ /home/undemocracy/undata/pdf/
</VirtualHost>

