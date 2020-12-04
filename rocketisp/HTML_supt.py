import time
from rocketisp.rocket_isp import __version__


def getHead(task='Thruster Isp Calculation'):
      
    date_and_time = time.strftime("%A, %b %d, %Y at %I:%M%p")

    return '''<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="content-type" content="text/html; charset=iso-8859-1">
	<title>%s</title>
<style>
.isp_data {
    font-family: "Lucida Console", Courier, monospace;
    border-collapse: collapse;
    font-weight: bold;
}

.alt_data {
    font-family: "Lucida Console", Courier, monospace;
    border-collapse: collapse;
    font-weight: normal;
}

.desc_data{
    font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
}

.summ_data{
    background-color: #FFFFFF;
    font-family: "Lucida Console", Courier, monospace;
    border-collapse: collapse;
    font-weight: bold;
    margin-bottom: 8px;
}

tbody tr:nth-child(odd) {
    color: #000000;
    background-color: #DBE4EE;
}

tbody tr:nth-child(even) {
    color: #000000;
    background-color: #F5F7FA;
}


.header {
	font-size: 22px;
	color: #000000;
	font-weight: bold;
	line-height: 26px;

}

.h_msg {
	font-size: 18px;
	color: #000000;
	font-weight: bold;
	line-height: 22px;
	margin-bottom: 8px;
}



</style>

</head>
<body>
<center><table bgcolor="#FFFFFF" width=100%%><tr><td colspan="2" nowrap align="center">
<h3 class="header">%s</h3></td></tr>
<tr>
<td align="left"><span class="header"></span></td>
<td align="right"><span class="header"></span></td></tr>
<tr>
<td align="left"><span class="h_msg"> RocketIsp %s</span></td>
<td align="right"><span class="h_msg">%s</span></td>
</tr></table></center>
'''%(task, task, 'version '+__version__, date_and_time)


def getFooter():
    return '''</body>
</html>
'''

