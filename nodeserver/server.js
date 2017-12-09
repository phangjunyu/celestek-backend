// server.js

// BASE SETUP
// =============================================================================

// call the packages we need
var express    = require('express');        // call express
var app        = express();                 // define our app using express
var bodyParser = require('body-parser');
var S3 = require('aws-sdk/clients/s3');
var PythonShell = require('python-shell');

// configure app to use bodyParser()
// this will let us get the data from a POST
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

var port = process.env.PORT || 8080;        // set our port

// ROUTES FOR OUR API
// =============================================================================
var router = express.Router();              // get an instance of the express Router

// test route to make sure everything is working (accessed at GET http://localhost:8080/api)
router.get('/', function(req, res) {
    res.json({ message: 'hooray! welcome to our api!' });
});
// more routes for our API will happen here

// router.post('/sendCoordinates', function(req, res, next){
// 	var coordinates = req.body
// 	var options = {
//   	// args: [coordinates]
// 	};
// 	PythonShell.run('hello.py', options, function (err) {
// 	  if (err) throw err;
// 		res.json(200)
// 	});
// })

router.get('/getProcessedImages', function(req, res, next){
	var options = {
  	// args: [coordinates]
	};
	// PythonShell.run('./imageDownload/get_images.py', options, function(err, results){
	// 	if (err) throw err;
	// 	console.log(">>>>>>>>>>>>>>>>>>", results)
	// })
	var pyshell = new PythonShell('./imageDownload/get_images.py')
	pyshell.on('message', function (message) {
	// received a message sent from the Python script (a simple "print" statement)
	console.log(message);
});

})

// REGISTER OUR ROUTES -------------------------------
// all of our routes will be prefixed with /api
app.use('/api', router);

// START THE SERVER
// =============================================================================
app.listen(port);
console.log('Magic happens on port ' + port);
