var galleryController = function(title) {
    var aws = require('aws-sdk'); //aws api를 사용하기위해 추가
    var multer = require('multer'); //파일업로드를 도와주는 multer모듈추가
    var multerS3 = require('multer-s3');//업로드한 파일을 S3에 바로 저장시키기위한 multer-s3

    //s3프로토콜을 위한 정보 기입
    var ep = new aws.Endpoint('https://s3.us-south.cloud-object-storage.appdomain.cloud');
    var s3 = new aws.S3({endpoint: ep, region: 'us-south'});
    //cos bucket name
    var myBucket = 'web-images-bucket';

    var upload = multer({
        storage: multerS3({
            s3: s3,
            bucket: myBucket,
            key: function (req, file, cb) {
                cb(null, file.originalname);
                console.log(file);
            }
        })
    });

    var getGalleryImages = function (req, res) {

        var imageUrlList = [];
        var params = {Bucket: myBucket};
        //버킷에 있는 개체의 데이터를 반환
        s3.listObjectsV2(params, function (err, data) {
            if(data) {
                var bucketContents = data.Contents;
                //버킷에 들어있는 데이터 개수만큼
                for (var i = 0; i < bucketContents.length; i++) {
                    var bcKey=bucketContents[i].Key;
                    //파일확장자 jpg png gif만 처리
                    if(bcKey.search(/.jpg/) > -1||bcKey.search(/.png/) > -1||bcKey.search(/.gif/) > -1) {
                        var urlParams = {Bucket: myBucket, Key: bucketContents[i].Key};
                        //개체의 버킷 이름 및 키를 전달하면 모든 개체에 대해 서명된 URL을 반환
                        s3.getSignedUrl('getObject', urlParams, function (err, url) {
                            imageUrlList[i] = url;
                        });
                    }
                }
            }
            //galleryView.ejs로 렌더링
            res.render('galleryView', {
                title: title,
                imageUrls: imageUrlList
            });
        });
    };


    return {
        getGalleryImages: getGalleryImages,
        upload: upload
    };
};

module.exports = galleryController;



/*
***in aws-sdk recent ver. ^2.437.0***

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
                    var bcKey=bucketContents[i].Key;
                    if(bcKey.search(/.jpg/) > -1||bcKey.search(/.png/) > -1||bcKey.search(/.gif/) > -1) {
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
*/
