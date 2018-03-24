// Template.home

Template.home.onCreated(function () {
  // TODO: do some stuff to connect to the Arduino and then run:
  // FlowRouter.go("productDetail");
});

// Template.productDetail

Template.productDetail.onCreated(function () {
  let instance = this;

  instance.transcript = new ReactiveVar("");
  instance.transcriptFinalized = new ReactiveVar(false);
  instance.listening = new ReactiveVar(false);
  instance.recastResult = new ReactiveVar(null);
  instance.language = new ReactiveVar("English");

  // https://github.com/ArnaudGallardo/transcripter/blob/d231930043b9bdb603bc41b29cfcc2e3fbedf2c5/transcripter/client/room.js
  instance.recognition = new webkitSpeechRecognition();
  instance.recognition.continuous = true;
  instance.recognition.interimResults = true;

  instance.recognition.onresult = function (event) {
    for (var i = event.resultIndex; i < event.results.length; ++i) {
      let result = event.results[i];
      let { transcript } = result[0];

      instance.transcriptFinalized.set(result.isFinal);
      instance.transcript.set(transcript);

      if (result.isFinal) {
        Meteor.call("getRecastIntent", transcript, instance.language.get(),
            (error, result) => {
          console.log("result:", result);
          instance.recastResult.set(result);
        });
      }
    }
  };
  instance.recognition.onerror = function(event) {
    console.log('error', event);
  };

  instance.autorun(() => {
    if (instance.listening.get()) {
      instance.recognition.start();
    } else {
      instance.recognition.stop();
    }
  });

  instance.autorun(() => {
    instance.recognition.lang =
        instance.language.get() === "English" ? "en" : "fr";

    if (instance.listening.get()) {
      instance.recognition.stop();
      Meteor.setTimeout(() => {
        instance.recognition.start();
      }, 1000);
    }
  });
});

Template.productDetail.onDestroyed(function () {
  instance.recognition.stop();
});

Template.productDetail.onRendered(function () {
  let instance = this;

  // TODO: connect to webcam and do it live

  // instance.recognition.lang = instance.data.language;
});

Template.productDetail.helpers({
  getTranscript() {
    return Template.instance().transcript.get();
  },
  getTranscriptFinalized() {
    return Template.instance().transcriptFinalized.get();
  },
  isListening() {
    return Template.instance().listening.get();
  },
  recastSlugIs(compareSlug) {
    let { intent } = Template.instance().recastResult.get();

    if (intent) {
      return intent.slug === compareSlug;
    }
  },
  recastSlugKnown() {
    let result = Template.instance().recastResult.get();

    if (!result || !result.intent) return false;

    return [
      "greetings",
      "ask-color-question",
      "change-shirt-color",
    ].indexOf(result.intent.slug) !== -1;
  },
  getRecastResult() {
    return Template.instance().recastResult.get();
  },
  getLanguage() {
    return Template.instance().language.get();
  },
  recastColor() {
    let { entities } = Template.instance().recastResult.get();

    return entities && entities.color && entities.color[0].raw.toLowerCase();
  },
});

Template.productDetail.events({
  "click .toggle-listening"(event, instance) {
    instance.listening.set(!instance.listening.get());
  },
  "click .select-english"(event, instance) {
    instance.language.set("English");
  },
  "click .select-french"(event, instance) {
    instance.language.set("French");
  },
});
