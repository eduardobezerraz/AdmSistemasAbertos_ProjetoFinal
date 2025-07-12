<?php
$config['imap_host'] = 'ssl://mail';
$config['smtp_server'] = 'tls://mail';
$config['imap_port'] = 993;
$config['smtp_port'] = 587;
$config['smtp_user'] = '%u';
$config['smtp_pass'] = '%p';
$config['smtp_auth_type'] = 'LOGIN';
$config['default_host'] = 'ssl://mail';
$config['default_port'] = 993;
$config['smtp_conn_options'] = [
  'ssl' => [
    'verify_peer' => false,
    'verify_peer_name' => false,
    'allow_self_signed' => true
  ]
];
$config['imap_conn_options'] = [
  'ssl' => [
    'verify_peer' => false,
    'verify_peer_name' => false,
    'allow_self_signed' => true
  ]
];
$config['mail_domain'] = 'sonserina.br';
