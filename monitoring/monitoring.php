<?php

$db_host = 'host.com';
$dbname = 'db name';
$db_user = 'db user';
$db_pswd = 'db pass';

try
{
  $bdd = new PDO('mysql:host='.$db_host.';dbname='.$db.';charset=utf8', $db_user, $db_pswd, array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
}
catch (Exception $e)
{
        die('Erreur : ' . $e->getMessage());
}

?>


<html>
<head>
	<meta charset="UTF-8">
</head>

<table>
	<tr>
		<th>Nom du serveur</th>
		<th>Statut</th>
		<th>En réparation</th>
		<th>Derniere Vérification</th>
	</tr>

<?php

$reponse = bdd->query('SELECT * FROM 'gameservers');

while ($donnees = $reponse->fetch())
{
	if($donnees['status'] == '1')
	{
		$statut = "Up"
	}
	else
	{
		$status = "Down"
	}

	if($donnees['inRepair'] == '1')
        {
                $inRepair = "Oui"
        }
        else
        {
                $inRepair = "Non"
        }
	echo '<tr>   <th>'.$donnees['gameName'].'</th> <th>'.$statut.'</th> <th>'.$inRepair.'</th> <th>'.$donnees['lastChecked'].'</th>   </tr>';
}

?>

</table>
</html>
