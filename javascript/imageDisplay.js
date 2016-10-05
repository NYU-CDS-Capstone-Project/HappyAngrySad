var currentPicIndex =1;
var img;
var emotions = ['angry','contempt','discust','fear','happy','neutral','sad','surprise'];
var faces =[];
var canvas;

var mainImage;
var button;

// function preload()
// {
//   // load image
//    img = loadImage("./images/1.jpg");

//   console.log(emoticons);

// }
 
function setup() 
{
  canvas = createCanvas(windowWidth, windowHeight);
  //noLoop();
var imageSize =500;
	imageString="./images/"+ (currentPicIndex+1)+ ".jpg";
	mainImage = createImg(imageString);
	mainImage.position(width/4,height/4);
	mainImage.size(imageSize, imageSize);

  button = createButton('Next');
  button.position(width/4 +imageSize +50, height/4 +imageSize /2);
  button.size(75,50);
  button.mousePressed(getNextPic);

  makeEmotionIcons()
//getNextPic()


//set up webcam
  // video = createCapture(VIDEO);
  // video.size(320, 240);
  // video.position(width/2, 0);
}
 
function draw() {
 
}

function facePressed(input){
	console.log(this.elt);
	$(this).css("background-color","#FFF");
}
function getNextPic(){
	//can do something more intelligent later
	imageString="./images/"+ (currentPicIndex+1)+ ".jpg";
	mainImage.elt.src = imageString;
	  // img.position(width/2,height/2);
	  // img.size(imageSize, imageSize);
	currentPicIndex=(currentPicIndex+1)%9;
}


function makeEmotionIcons(){
	console.log("making emoitons");
	pics = [];
	textSize(12);
  var imageSize =50;
  var padding =20;
  for (var i = 0; i<emotions.length;i++){
  	 var img = createImg("./icons/"+ emotions[i] + ".jpg");
  	 console.log(img);
	  img.position(width/4+i*imageSize + i*padding,height/4 + mainImage.size().height);
	  img.size(imageSize, imageSize);
	  img.class("emoticon")
	  img.id(emotions[i]);
	//   //canvas.position(300, i*imageSize + i*padding,height/2);
	 
	  var text = createDiv(emotions[i]);
      text.position(width/4+i*imageSize + i*padding,height/4 + mainImage.size().height + 50);
      faces.push([img,text]);
  }

}


function windowResized() {
  resizeCanvas(windowWidth, windowHeight);  
  console.log("resizing");
  resizeImages();
}

function resizeImages(){
	var imageSize =50;
  var padding =20;
  for (var i = 0; i<faces.length;i++){
  	faces[i][0].position(width/4+i*imageSize + i*padding,height/4 + mainImage.size().height);
  	faces[i][1].position(width/4+i*imageSize + i*padding,height/4 + mainImage.size().height + 50);
}
	mainImage.position(width/4,height/4);
	button.position(width/4 + mainImage.size().width  +50, height/4 + mainImage.size().width  /2);


}