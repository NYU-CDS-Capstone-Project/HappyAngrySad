var faces;

$(document).ready(function() {
    var isChrome = !!window.chrome && !!window.chrome.webstore;
    var isFirefox = typeof InstallTrigger !== 'undefined';
    var isOpera = (!!window.opr && !!opr.addons) || !!window.opera || navigator.userAgent.indexOf(' OPR/') >= 0;
    var faces;
    if (isChrome || isFirefox || isOpera) {
        //JSSDKDemo.init();
        JSSDKDemo.run();
    } else {
        JSSDKDemo.create_alert("incompatible-browser", "It appears that you are using an unsupported browser. Please try this demo on Chrome, Firefox, or Opera.");
    }
});

var JSSDKDemo = (function() {
    var detector = null;

    var face_visible = true;

    // function to post response from affectiva -  aggregates data before posting
    
    var run = function() {
        var facevideo_node = document.getElementById("facevideo-node");
        detector = new affdex.CameraDetector(facevideo_node);
        
        // classes of data we can get
        detector.detectAllEmotions();
        detector.detectAllExpressions();
        detector.detectAllEmojis();
        detector.detectAllAppearance();

        detector.addEventListener("onWebcamConnectSuccess", function() {
            console.log("msg-starting-webcam");
        });
        
        detector.addEventListener("onWebcamConnectFailure", function() {
          console.log("webcam connected"); 
          });
        
        if (detector && !detector.isRunning) {
            detector.start();
        }
        

      //   function drawFeaturePoints(img, featurePoints) {
      //   var contxt = $('#face_video_canvas')[0].getContext('2d');

      //   var hRatio = contxt.canvas.width / img.width;
      //   var vRatio = contxt.canvas.height / img.height;
      //   var ratio = Math.min(hRatio, vRatio);

      //   contxt.strokeStyle = "#FFFFFF";
      //   for (var id in featurePoints) {
      //     contxt.beginPath();
      //     contxt.arc(featurePoints[id].x,
      //       featurePoints[id].y, 2, 0, 2 * Math.PI);
      //     contxt.stroke();

      //   }
      // }

        //get the video element inside the div with id "facevideo-node"
        // var face_video = $("#facevideo-node video")[0];

        // face_video.addEventListener("playing", function() {
        //   console.log("playing");
        //   });
        
        detector.addEventListener("onInitializeSuccess", function() {
            //load initial video
           
        });
        
        // everything to do when we get response back from affectiva
        var count =1;
        detector.addEventListener("onImageResultsSuccess", function(faces, image, timestamp) {
          faces =faces;
          if (count ==1){
          console.log(faces);
          count++;
        }
      //Draw the detected facial feature points on the image
      
        var feelings = ['joy','engagement','sadness','surprise','fear','valence','contempt'];
        emotionResponse = [];
        
        for( var i = 0 ; i< feelings.length;i++){
          console.log()
        emotionResponse.push(faces[0].emotions[feelings[i]]);

      }
      //graphDiv.data.push({x: [1,2,3,4], y: [4,3,2,1], mode: 'lines+markers'})
      data = [
        {
        
            x:feelings,
            y:emotionResponse,
            type :"bar",
            
        }
      ];
      layout= {
              yaxis: {
                range: [0, 100]
              }

            };

        Plotly.newPlot('myDiv', data, layout);



        });
    };

    
    var begin_capture = function() {
       
        
    };
    
    var stop_capture = function() {
        stop_time = get_current_time_adjusted();
        capture_frames = false;
        detector.stop();
             
    };
    
    
    
     return {
         init: function() {
            
  
         },

         run: run,

        responses: function(clicked_id) {
           
        },
        
        //create_alert: create_alert
    };
})();
