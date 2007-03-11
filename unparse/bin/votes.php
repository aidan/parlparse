<?php
// Datebase stuff, used later on
$con = mysql_connect( "localhost","","");
if (!$con) {
  die("Can't connect to datebase: ".mysql_error());
}
mysql_select_db("", $con);


// Set up the file paths
$filepath = "/home/sym/un/undata/html";
$dir = opendir($filepath);


// Loop though all files
while ( false !== ( $file = readdir( $dir))) {
  // if the file has been indexed...
  if (substr($file,-4,4 ) == "html" && substr($file,-14,14) != "unindexed.html") {
    $file_string = file_get_contents($filepath."/".$file);
    // if there is a vote  in the file...
    if (preg_match_all('/<div class="recvote" id="(.*?)">(.*?)<\\/div>/s',$file_string, $matches)) {
      // Grab the date from the file
      preg_match('/<span class="code">(.*?)<\\/span> <span class="date">(.*?)<\\/span> <span class="time">(.*?)<\\/span>/s', $file_string, $file_info);
      $code = $file_info[1];
      $date = $file_info[2];
      $time = $file_info[3];

      // Loop though all votes in a file.
      foreach($matches[1] as $vote_no => $para_id) {
        // Grab the votes and information about the vote:
        // motion text
        preg_match('/<p class="motiontext">(.*?)<\\/p>/s',$matches[2][$vote_no], $vote_motion_text);
        // count text
        preg_match('/<p class="votecount">(.*?)<\\/p>/s',$matches[2][$vote_no], $vote_count_text);
        // vote list
        preg_match('/<p class="votelist">(.*?)<\\/p>/s', $matches[2][$vote_no], $votelist);
        // Put every vote in to the $votes array
        preg_match_all('/<span class="(.*?)">(.*?)<\\/span>/', $votelist[1], $votes);
        
        // Deal with the datebase stuff:
        // We will query the database for each file name and paragraph id
        // to make sure it's not there already
        $sql = "SELECT id FROM votes WHERE `file`='$file' AND `id`='$para_id'";
        $result = mysql_query($sql);

        // Grab the object
        $result = @mysql_fetch_object($result) ;
        // If there is nothing there, insert the new row
        if ( !$result ) {
          mysql_query("INSERT INTO votes (id,file,date,motion,count) VALUES ('$para_id','$file','$date','$vote_motion_text[1]','$vote_count_text[1]')");
          
          // Go though all the votes and insert them in to vote_records
          for ($i =0;$i<sizeOf($votes[0]);$i++) {
            $member = $votes[2][$i];
            $vote = $votes[1][$i];
            mysql_query("INSERT INTO vote_records (file,id,member,vote) VALUES ('$file','$para_id','$member','$vote')");
          }
        }
      }
    }
  }
}
mysql_close($con);
