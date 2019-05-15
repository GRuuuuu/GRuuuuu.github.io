var rateLimit = 0;

function getAllImageDocuments() {
  $.ajax({
      url: cloudantURL.origin + "/" + imageDatabase + "/_all_docs",
      type: "GET",
      headers: {
        "Authorization": "Basic " + btoa(cloudantURL.username + ":" + cloudantURL.password)
      },
      success: function (data) {
        for (var index in data.rows) {
          getImage(data.rows[index].id)
        }
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.log(errorThrown);
        console.log(textStatus);
        console.log(jqXHR);
      }
  });
}

function getImage(id) {
  var image = new Image();

  var imageSection = document.createElement('div');
  var imageHolder = document.createElement('div');
  image.className = "uploadedImage";
  loadAttachment(id,image);
  imageSection.id = id
  imageSection.className = "imageSection";
  imageHolder.className = "imageHolder";
  imageHolder.appendChild(image);
  imageSection.appendChild(imageHolder);
  uploadedImages.prepend(imageSection);
  getDocumentWithId(id, imageSection, 0);
}

function loadAttachment(id, dom) {
  if (rateLimit >= 5) {
    setTimeout(function() {
      loadAttachment(id,dom);
    }, 1000);
  } else {
    rateLimit++;

    console.log(rateLimit);
    $.ajax({
        url: cloudantURL.origin + "/" + imageDatabase + "/" + id + "/image",
        type: "GET",
        headers: {
          "Authorization": "Basic " + btoa(cloudantURL.username + ":" + cloudantURL.password)
        },
        xhr:function(){
          var xhr = new XMLHttpRequest();
          xhr.responseType= 'blob'
          return xhr;
        },
        success: function (data) {
          let url = window.URL || window.webkitURL;
          dom.src = url.createObjectURL(data);
          rateLimit--;
        },
        error: function (jqXHR, textStatus, errorThrown) {
          console.log(errorThrown);
          console.log(textStatus);
          console.log(jqXHR);
          rateLimit--;
        }
    });
  }
}


getAllImageDocuments();

// var localDB = new PouchDB('test');
// var remoteDB = new PouchDB("https://d1dda683-a71d-43ca-9c92-bf111700dc00-bluemix:fa2971ea3c351e710593bd1fb85d6b714dd5d2c9cdc03a49568f58fd8874cb1f@d1dda683-a71d-43ca-9c92-bf111700dc00-bluemix.cloudant.com/test");
// localDB.info().then(function (info) {
//   console.log(info);
// });
// remoteDB.info().then(function (info) {
//   console.log(info);
// });
// localDB.sync(remoteDB).on('change', function (change) {
//   // yo, something changed!
//   console.log("something changed")
//   console.log(change)
// }).on('complete', function () {
//   // yay, we're done!
//   console.log("done")
// }).on('error', function (err) {
//   // boo, something went wrong!
//
//   console.log("error");
//   console.log(err);
// });;
