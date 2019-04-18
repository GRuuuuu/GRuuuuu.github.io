var galleryController = function(title) {
    var aws = require('aws-sdk'); //aws api를 사용하기위해 추가
    var multer = require('multer');
    var multerS3 = require('multer-s3');
    //s3프로토콜을 위한 정보 기입
    var ep = new aws.Endpoint('https://s3.us-south.cloud-object-storage.appdomain.cloud');
    var s3 = new aws.S3({
        endpoint: ep, 
        region: 'us-south',
        accessKeyId:'b01c551bb9604c8ebc22fefe36e4fbc7',
        secretAccessKey:'06d88e8c4d75adba1d51ce863144fe29b02d6fcb36c15f39'
    });

    //cos bucket name
    var myBucket = '190418testbucket';

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
        var params = {Bucket: myBucket};
        //버킷에 있는 개체의 데이터를 반환
        s3.listObjectsV2(params, function (err, data) {
            if(data) {
                console.log("listing " + myBucket, [err, JSON.stringify(data)]);
            }
        });
    };

    var createBucket=function(req,res){
        var params = {Bucket: '190418testbucket2'};
        s3.createBucket(params, function(err,data) {
            console.log("checking for error on createBucket " + params.Bucket, err);
            console.log("checking for data on createBucket " + params.Bucket, JSON.stringify(data));
        });
    };

    var putObject=function(req,res){
        var data = {Bucket: myBucket, Key: 'test.txt', Body: require('fs').createReadStream('./hellohello.txt')};
        s3.putObject(data, function(err, data) {
          if (err) {
           console.log("Error uploading data: ", err);
          } else {
           console.log("Successfully uploaded file to " + myBucket);
           console.log("checking for data "+ JSON.stringify(data));
          }
         
        });
    };

    var delObject=function(req,res){
        var itemsToDelete = Array();
            itemsToDelete.push ({ Key : 'hellohello.txt' });
        var params = {Bucket: myBucket,
            Delete: {
                Objects: itemsToDelete,
                Quiet: false}};
        s3.deleteObjects(params, function(err, data) {
            if (err) {
             console.log("Error data: ", err);
            } else {
             console.log("checking for data "+ JSON.stringify(data));
            };
        });
    }
    var delBucket=function(req,res){
        var params={Bucket:myBucket};
        s3.deleteBucket(params, function(err, data) {
            if (err) {
                console.log("Error data: ", err);
               } else {
                console.log("checking for data "+ JSON.stringify(data));
               };
          });
    }
    return {
        getGalleryImages: getGalleryImages,
        createBucket: createBucket,
        upload: upload,
        putObject:putObject,
        delObject:delObject,
        delBucket:delBucket
    };
};

module.exports = galleryController;


