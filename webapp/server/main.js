import * as recastai from "recastai";
import Future from 'fibers/future';

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
      future.return({
        intent: res.intent(),
        entities: res.entities,
      });
    });

    return future.wait();
  },
});
