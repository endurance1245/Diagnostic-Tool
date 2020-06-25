// Taking workflow details only when workflow radio button is clicked
function workflowradio(){
    $('#Workflowdetails').show()
}

function databaseradio(){
    $('#Workflowdetails').hide()
}

// To take the problem details of the user
function getProblem() {
    $('#errorblock').hide()
    $('#outputcomplete').hide()
    $('#loader').hide()
    $('#triggerloader').hide()
    document.getElementsByName('output')[0].value="Welcome to Campaign Diagnostic Tool!";
    var instance = document.getElementById("Instancename").value;
    var configuration = {}
    var username = document.getElementById("username").innerHTML;
    configuration["userldap"] = username
    console.log(instance)
    if (instance === "")
    {
        alert("Enter Instance Name");
    }
    if (document.getElementById("Database").checked && instance !== ""){
        var problem = document.getElementById("Database").value;
    }
    if (document.getElementById("Workflow").checked &&  instance !== "")
    {
        $('#Workflowdetails').show()
        if (document.getElementById("WorkflowSingle").checked)
            var workflowtype = "Single"
        else
        {
            var workflowtype = "Multiple"
            var problem = document.getElementById("WorkflowMultiple").value
        }
        if (workflowtype === "Single")
        {
            var problem = document.getElementById("WorkflowSingle").value
            var workflowid =document.getElementById("Workflowvalue").value;
            if (workflowid === "")
                alert("Enter Workflow sinternal label as you have selected single workflow");
            console.log(workflowid)
            configuration["workflow_name"] = workflowid
        }
    }
    if(problem)
    {
        const timestamp = strptime();
        var host = instance.split('.campaign')
        if (instance!=host[0])
            instance = host[0]
        $('#outputbox').show()
        RTest(instance, problem, timestamp, configuration)    
    }

    console.log(problem)
}

// to output to the user by hitting the output api  5 time after every interval of 30s
function showDAGOutput(problem, runId){
    $('#triggerloader').hide()
    $('#loader').show()
    $('#outputtable').show()
    var timesRun = 0;
    var interval = setInterval(function(){
    timesRun += 1;
    console.log(timesRun)
    if(timesRun === 5){
        console.log("stopping")
        console.log("hidden")
        $('#loader').hide()
        $('#outputcomplete').show()
        clearInterval(interval);
    }
    // if(timesRun === 2)
    // {
    //     $('#outputtable').hide()
    // }
    
    getOutput(problem, runId)
    //do whatever here..
    }, 30000);
}

//to do the rtest on the host
function RTest(instance, problem, timestamp, configuration){
    var apiUrl = 'https://diagnostictool.camp-infra.adobe.net/diagnostictool/checkinstance/'+instance+'.campaign.adobe.com';
    console.log(apiUrl);
    $('#outputbox').show()
    fetch(apiUrl,{
        method: "GET",
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    }).then(response => {
        console.log("Response in rtest")
        console.log(response)
        return response.json()
    }).then(data => {
        // if (('localHost' in data)==true)
        console.log("data in rtest")
        console.log(data)
        localHost = data["localHost"]
        build = data["build"]
        configuration["build"] = build
        pausedDag(localHost, problem, timestamp, configuration)
        return data;
    }).catch(err => {
        console.log("error");
        res = err
        alert("Enter correct Instance URL")
        return err
    });
}

// to check if the dag is paused or not
function pausedDag(instance, problem, timestamp, configuration){
    $('#triggerloader').show()
    var apiUrl = 'https://diagnostictool.camp-infra.adobe.net/diagnostictool/tasks/'+problem+'/paused';
    console.log(apiUrl);
    fetch(apiUrl,{
        method: "GET",
        headers: {
            'Accept': 'application/json',
            "Content-Type": 'application/x-www-form-urlencoded',
        }
    }).then(response => {
        console.log("Response in paused dag")
        console.log(response)
        return response.json()
    }).then(data => {
        // Work with JSON data here
        console.log("data in paused dag")
        console.log(data["is_paused"])
        if (data["is_paused"]===false)
        {
            document.getElementsByName('output')[0].value=document.getElementsByName('output')[0].value+"\nWe are set to trigger the dag";
            checkRunningDag(instance, problem, timestamp, configuration)
        }
        else
        {
            document.getElementsByName('output')[0].value=document.getElementsByName('output')[0].value+"\nError Occured! DAGs are paused, Try again";
        }

    }).catch(err => {
        // Do something for an error here
        $('#triggerloader').hide()
        $('#errorblock').show()
        console.log("error");
        document.getElementsByName('output')[0].value=document.getElementsByName('output')[0].value+"\nError Occured! DAGs are paused";
    });
}


// to check if there is already a dag running
function checkRunningDag(instance, problem, timestamp, configuration){
    var apiUrl = 'https://diagnostictool.camp-infra.adobe.net/diagnostictool/tasks/'+problem+'/check_dag_run/'+timestamp+'/'+instance;
    console.log(apiUrl);
    fetch(apiUrl,{
        method: "GET",
        headers: {
            'Accept': 'application/json',
            "Content-Type": 'application/x-www-form-urlencoded',
        }
    }).then(response => {
        console.log("Response in check running dag")
        console.log(response)
        return response.json()
    }).then(data => {
        console.log("data in check running dag")
        console.log(data)
        if (data["is_running"]===true)
         {
            var runId = data["run_id"]
            console.log("already running")
            console.log(runId)
            showDAGOutput(problem, runId)
         }
        else
            triggerDag(instance, problem, timestamp, configuration)
        return data;
    }).catch(err => {
        // Do something for an error here
        $('#triggerloader').hide()
        $('#errorblock').show()
        console.log("error");
        document.getElementsByName('output')[0].value=document.getElementsByName('output')[0].value+"\nError Occured while Trigger!";
        return err
    });
}

//to trigger the dag 
function triggerDag(instance, problem, timestamp, configuration){
    console.log(configuration)
    runId =  instance + "&" +problem+ "&" + timestamp
    console.log(runId)
    var apiUrl = 'https://diagnostictool.camp-infra.adobe.net/diagnostictool/tasks/'+problem+'/trigger';
    console.log(apiUrl);
    fetch(apiUrl,{
        method: "POST",
        headers: {
            'Accept': 'application/json',
            "Content-Type": 'application/x-www-form-urlencoded',
        },
        body:JSON.stringify({
            "run_id" : runId,
            "execution_date": timestamp,
            "conf": configuration,
        })
    }).then(response => {
        console.log("response in trigger");
        console.log(response);
        document.getElementsByName('output')[0].value=document.getElementsByName('output')[0].value+"\nDAG is triggered"
        return response.json()
    }).then(data => {
        // Work with JSON data here
        console.log("data in trigger");
        console.log(data);
        document.getElementsByName('output')[0].value=document.getElementsByName('output')[0].value+"\nTrigger Message : "+JSON.stringify(data, undefined, 4);
        showDAGOutput(problem, runId)
        return data;
    }).catch(err => {
        // Do something for an error here
        $('#triggerloader').hide()
        $('#errorblock').show()
        console.log("error");
        document.getElementsByName('output')[0].value=document.getElementsByName('output')[0].value+"\nError Occured while Trigger!";
        return err
    });
}

// to get the output
function getOutput(problem_id, runId) {
    var apiUrl = 'https://diagnostictool.camp-infra.adobe.net/diagnostictool/tasks/' + problem_id + '/' + runId;
    console.log(apiUrl);
    fetch(apiUrl,{
        method: "GET",
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    }).then(response => {
        console.log("response in output");
        console.log(response);
        return response.json();
    }).then(data => {
        // Work with JSON data here
        
        console.log("data in output");
        console.log(data);
        if(data==="{}")
        {
            document.getElementsByName('output')[0].value=document.getElementsByName('output')[0].value + "Error Occured while running DAG\n"
        }
        else{
            displayOutput(data);
        }
        // document.getElementsByName('output')[0].value="DAGs Output:\n"+ JSON.stringify(data, undefined, 4);
        return data;
    }).catch(err => {
        // Do something for an error here
        $('#loader').hide()
        $('#errorblock').show()
        document.getElementsByName('output')[0].value=document.getElementsByName('output')[0].value + "Error Occured in DAG\n"
    });
}

function strptime(){
    var now = new Date;
    year = now.getUTCFullYear();
    month = now.getUTCMonth();
    day = now.getUTCDate();
    hr = now.getUTCHours();
    min = now.getUTCMinutes();
    sec = now.getUTCSeconds();
    msec = now.getUTCMilliseconds();
    if (month<10)
    mon= '0'+ (month+1);
    if (day<10)
    day ='0'+ day;
    var hr = addZero(now.getUTCHours(), 2);
    var min = addZero(now.getUTCMinutes(), 2);
    var sec = addZero(now.getUTCSeconds(), 2);
    // var msec = addZero(now.getUTCMilliseconds(), 3);
    var stamp = year.toString() + "-" + mon.toString() + '-' + day.toString() + 'T' + hr.toString()
            +':'+ min.toString()+ ':'+sec.toString()
            // +'.'+msec.toString();
    console.log(stamp)
    return stamp;
    }
    function addZero(x,n){
        while (x.toString().length < n) {
            x = "0" + x; 
            }
        return x;
}

function displayOutput(data)
   {
    var table = document.getElementById("outputtable")
    $('#outputtable tr:gt(0)').remove() 
    
    var i =  1
    for (var key in data){
        var row = table.insertRow(i);
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var value = JSON.stringify(data[key], undefined, 4)
        cell1.className = 'td';
        cell2.className = 'td';
        cell1.innerHTML = key
        cell2.innerHTML = value
        i = i+1
    }
}
