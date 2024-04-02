CREATE USER IF NOT EXISTS 'wagtail'@'localhost' IDENTIFIED BY 'your_password';
CREATE DATABASE beobgrp_site;
GRANT ALL PRIVILEGES ON beobgrp_site.* TO 'wagtail'@'localhost';
FLUSH PRIVILEGES;

