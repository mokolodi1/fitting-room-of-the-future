function defaultAction(templateName, params) {
  // renders appBody with templateName inside
  BlazeLayout.render("appBody", { content: templateName, params });
}

function sameNameAndAction(name) {
  return {
    name,
    action: _.partial(defaultAction, name)
  };
}

FlowRouter.route("/", sameNameAndAction("home"));
FlowRouter.route("/detail", sameNameAndAction("productDetail"));
