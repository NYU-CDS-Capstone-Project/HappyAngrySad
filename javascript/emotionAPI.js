
 //apiKey: Replace this with your own Project Oxford Emotion API key, please do not use my key. I include it here so you can get up and running quickly but you can get your own key for free at https://www.projectoxford.ai/emotion 
 var apiKey = "69d79b998b684114ba55585b376c60ba";
 
 //apiUrl: The base URL for the API. Find out what this is for other APIs via the API documentation
 var options = "perFrame";
 var apiUrl = "https://api.projectoxford.ai/emotion/v1.0/recognize";
 
 
 function CallAPI(file, apiUrl, apiKey)
 {
	 $.ajax({
	 url: apiUrl,
	 beforeSend: function (xhrObj) {
	 console.log(xhrObj);
	 xhrObj.setRequestHeader("Content-Type", "application/octet-stream");
	 xhrObj.setRequestHeader("Ocp-Apim-Subscription-Key", apiKey);
	 },
	 type: "POST",
	 data: file,
	 processData: false
	 })
	 .done(function (response) {
	 ProcessResult(response);
	 })
	 .fail(function (error) {
	 $("#response").text(error.getAllResponseHeaders());
	 });
 }
 
 function ProcessResult(response)
 {
 data = JSON.stringify(response);
 $("#response").text(data);
 console.log(data);
 }
