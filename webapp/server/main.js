import * as recastai from "recastai";
import Future from 'fibers/future';
import * as fs from 'fs';

const enClient = new recastai.request('2b18eed7e1c716f8a269bae8664a6a2d', 'en');
const frClient = new recastai.request('2b18eed7e1c716f8a269bae8664a6a2d', 'fr');

Meteor.methods({
  getRecastIntent(transcript, language) {
    console.log("language, transcript:", language, transcript);
    var future = new Future();

    let client;

    if (language === "English") {
      client = enClient;
    } else {
      client = frClient;
    }

    client.analyseText(transcript).then(function(res) {
      console.log("res.intent():", res.intent());

      let intent = res.intent();
      if (intent && intent.confidence > .6 &&
          intent.slug === "change-shirt-color" &&
          res.entities.color) {
        console.log("res.entities:", res.entities);
        fs.writeFile("/tmp/over_here_arnaud", res.entities.color[0].rgb,
            function(err) {
          if(err) {
            console.log("err:", err);
          }

          console.log("The file was saved!", res.entities.color[0].rgb);
        });
      }

      future.return({
        intent,
        entities: res.entities,
      });
    });

    return future.wait();
  },
});
