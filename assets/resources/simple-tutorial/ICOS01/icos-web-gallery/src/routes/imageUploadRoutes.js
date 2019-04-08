var express = require('express');
var imageUploadRouter = express.Router();
var status = '';

var router = function(title) {

    var galleryController =
        require('../controllers/galleryController')(title);

    imageUploadRouter.route('/')

        .post(
            galleryController.upload.array('img-file', 1), function (req, res, next) {

                if(res.statusCode===200 && req.files.length > 0) {
                    status = 'uploaded file successfully';
                }
                else {
                    status = 'upload failed';
                }
                res.render('index', {status: status, title: title});
            });


    return imageUploadRouter;
};

module.exports = router;