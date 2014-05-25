<HTML>
<HEAD>
<TITLE>Team PHP Script to Connect to SqlLite3 DB</TITLE>
</HEAD>
<BODY>

<?php

/* the above "<?php" signals that the PHP script has begun */		

$today = date("Y-m-d");	

PRINT "<CENTER>Today is: $today.</CENTER>";

PRINT "<BR />";


?>

/* This is a simple example of opening up the DB and selecting the first row for everything that is in the DB by ordinal values row[0] gives just the first column */ <BR />
<?php


$dir = 'sqlite:database/schedule.db';

PRINT "<BR />The dir that the DB resides in and the command that open it is: $dir<BR />";

$dbh  = new PDO($dir) or die("cannot open the database");

$query =  "SELECT * FROM user";

foreach ($dbh->query($query) as $row)
{
    PRINT "$row[0]<BR />";
}

?>


<BR />/* This example will insert some values into the DB which you will see on the next select statement */<BR />
<?php

$dir = 'sqlite:database/schedule.db';

$dbh  = new PDO($dir) or die("cannot open the database");

$query = "insert into user values('clampitc','Charles','Clampitt','Student');";

$dbh->query($query);

$query = "insert into event values('clampitc',' 2014-05-02 03:30:00',' 2014-05-02 09:00:00','Some Atrrib','Pearl District','PhotoShoot',0);";

$dbh->query($query);

PRINT "Update complete";

?>


<BR />/* This is an example of selecting from the DB rows by column name. The user table structure is onid_id varchar(8),fname varchar(20),lname varchar(40),dept varchar(40) */<BR />
<?php

$dir = 'sqlite:database/schedule.db';

$dbh  = new PDO($dir) or die("cannot open the database");

$query =  "SELECT onid_id, fname, lname, dept FROM user";

foreach ($dbh->query($query) as $row)
{
    PRINT "<BR />$row[onid_id] $row[fname] $row[lname] $row[dept]";
}


?>

<BR /><BR />Some notes for the team. The way SQLLite3 works is just like writting SQL commands directly and executing them. From the command line or in code. 
<BR />So to update a or delete a value you use UPDATE or DELETE. The WHERE clause you must use a singe quote round the value you are looking for just like 
<BR />you would if you were writting a command in SQl management studio. So:

<BR /><BR /><BR />    UPDATE user SET onid_id='SomeValue' WHERE onid_id='schreibm';  
<BR /><BR /><BR />Remeber the ';' at the end of the line. Just insert this and execute it and you will have updated all instances in the user table where
<BR />the onid_id was equal to schreibm and now is would say SomeValue.



</BODY>
</HTML>