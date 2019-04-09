var express = require('express');
var imageUploadRouter = express.Router();
var status = '';

var router = function(title) {
    //galleryController를 가져옴
    var galleryController =
        require('../controllers/galleryController')(title);
        //현재위치 (https://url/)에서 post로 request
        imageUploadRouter.route('/')
        .post(
            //Controller의 uprload함수를 호출
            galleryController.upload.array('img-file', 1), function (req, res, next) {
                if(res.statusCode===200 && req.files.length > 0) 
                {//성공시
                    status = 'uploaded file successfully';
                }
                else 
                {//실패
                    status = 'upload failed';
                }
                //이상의 결과(status와 title)를 담아서 index.ejs에 렌더링
                res.render('index', {status: status, title: title});
            });
    return imageUploadRouter;
};
//app.js에서 해당 모듈을 require해서 사용할수있게 export
module.exports = router;