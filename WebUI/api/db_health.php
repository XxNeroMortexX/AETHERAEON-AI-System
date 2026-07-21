<?php
declare(strict_types=1);

ob_start();
ini_set('display_errors', '0');
ini_set('log_errors', '0');
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

$database_state = 'Offline';
$connection = null;

try {
    require dirname(__DIR__) . '/config/db_config.php';
    mysqli_report(MYSQLI_REPORT_OFF);
    $connection = @new mysqli(
        (string) $db_host,
        (string) $db_user,
        (string) $db_pass,
        (string) $db_name,
        (int) $db_port
    );

    if (!$connection->connect_errno) {
        $result = @$connection->query('SELECT 1');
        if ($result instanceof mysqli_result && $result->fetch_row() !== null) {
            $database_state = 'Online';
        }
        if ($result instanceof mysqli_result) {
            $result->free();
        }
    }
} catch (Throwable $ignored) {
    $database_state = 'Offline';
} finally {
    if ($connection instanceof mysqli) {
        @$connection->close();
    }
}

ob_clean();
echo json_encode(['database' => $database_state], JSON_UNESCAPED_SLASHES);
