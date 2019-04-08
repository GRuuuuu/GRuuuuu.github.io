var galleryController = function(title) {

    var aws = require('aws-sdk');
    var multer = require('multer');
    var multerS3 = require('multer-s3');
    var ep = new aws.Endpoint('https://s3.us-south.cloud-object-storage.appdomain.cloud');
    var s3 = new aws.S3({endpoint: ep, region: 'us-south'});
    var myBucket = 'web-images-bucket';


    var upload = multer({
        storage: multerS3({
            s3: s3,
            bucket: myBucket,
            key: function (req, file, cb) {
                cb(null, file.originalname);
                console.log(file);
                console.log(cb);
            }
        })
    });

    var getGalleryImages = function (req, res) {

        var imageUrlList = [];
        var params = {Bucket: myBucket};
        function getBucketData_promise(params){
            return new Promise(function(resolve, reject){
                s3.listObjectsV2(params, function (err, data) {
                    if(data) {
                        var bucketContents = data.Contents;
                        resolve(bucketContents);
                    }
                    else{
                        reject(err);
                    }
                });
            });
        }
        function getImageUrl_promise(urlParams){
            return new Promise(function(resolve, reject){
                s3.getSignedUrl('getObject', urlParams, function (err, url) {
                    if(url) {
                        resolve(url);
                    }
                    else{
                        reject(err);
                    }
                });
            });
        }
        getBucketData_promise(params)
            .then(async function(bucketContents){
                for (var i = 0; i < bucketContents.length; i++) {
                    if(bucketContents[i].Key.search(/.jpg/||/.png/) > -1) {
                        var urlParams = {Bucket: myBucket, Key: bucketContents[i].Key};
                        await getImageUrl_promise(urlParams)
                            .then(async function(url){
                                imageUrlList[i] = url;
                            });
                    }
                }
                return imageUrlList;
            })
            .then(function(urlData){
                res.render('galleryView', {
                    title: title,
                    imageUrls: urlData
                });
            });
    };
    return {
        getGalleryImages: getGalleryImages,
        upload: upload
    };
};

module.exports = galleryController;
