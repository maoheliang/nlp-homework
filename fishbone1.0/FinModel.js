function FinModel(id_, fid_, name_, upOrDown_, fontColor_, lineColor_, link_) {
  this.id_ = id_;
  this.fid_ = fid_;
  this.name_ = name_;
  this.finLength_ = "";
  this.nameLength_ = name_.length;
  this.leaf_ = "";
  this.finColor_ = "";
  this.lineColor_ = lineColor_;
  this.nameColor_ = fontColor_;
  this.click_ = null;
  this.link_ = link_;
  this.level_ = "";
  this.upOrDown_ = upOrDown_;
  this.fromNodePosition_ = null;
  this.toNodePosition_ = null;
  this.nextLevelCount_ = 0;
  this.nextLevelMaxLength_ = 0;
  this.nextLevel2MaxLength_ = 0;
  this.finTeam_ = 0;
  this.rotate_ = "";
  this.childrenNode_ = new Array();
  this.setId_ = function (id_) {
    this.id_ = id_;
  };
  this.getId_ = function () {
    return this.id_;
  };
  this.setFid_ = function (fid_) {
    this.fid_ = fid_;
  };
  this.getFid_ = function () {
    return this.fid_;
  };
  this.setName_ = function (name_) {
    this.name_ = name_;
  };
  this.getName_ = function () {
    return this.name_;
  };
  this.setFinLength_ = function (finLength_) {
    this.finLength_ = finLength_;
  };
  this.getFinLength_ = function () {
    return this.finLength_;
  };
  this.setNameLength_ = function (nameLength_) {
    this.nameLength_ = nameLength_;
  };
  this.getNameLength_ = function () {
    return this.nameLength_;
  };
  this.setFinColor_ = function (finColor_) {
    this.finColor_ = finColor_;
  };
  this.getFinColor_ = function () {
    return this.finColor_;
  };
  this.setNameColor_ = function (nameColor_) {
    this.nameColor_ = nameColor_;
  };
  this.getNameColor_ = function () {
    return this.nameColor_;
  };
  this.setLeaf_ = function (leaf_) {
    this.leaf_ = leaf_;
  };
  this.getLeaf_ = function () {
    return this.leaf_;
  };
  this.setLevel_ = function (level_) {
    this.level_ = level_;
  };
  this.getLevel_ = function () {
    return this.level_;
  };
  this.setUpOrDown_ = function (upOrDown_) {
    this.upOrDown_ = upOrDown_;
  };
  this.getUpOrDown_ = function () {
    return this.upOrDown_;
  };
  this.setFromNodePosition_ = function (fromNodePosition_) {
    this.fromNodePosition_ = fromNodePosition_;
  };
  this.getFromNodePosition_ = function () {
    return this.fromNodePosition_;
  };
  this.setToNodePosition_ = function (toNodePosition_) {
    this.toNodePosition_ = toNodePosition_;
  };
  this.getToNodePosition_ = function () {
    return this.toNodePosition_;
  };
  this.setNextLevelCount_ = function (nextLevelCount_) {
    this.nextLevelCount_ = nextLevelCount_;
  };
  this.getNextLevelCount_ = function () {
    return this.nextLevelCount_;
  };
  this.setNextLevelMaxLength_ = function (nextLevelMaxLength_) {
    this.nextLevelMaxLength_ = nextLevelMaxLength_;
  };
  this.getNextLevelMaxLength_ = function () {
    return this.nextLevelMaxLength_;
  };
  this.setNextLevel2MaxLength_ = function (nextLevel2MaxLength_) {
    this.nextLevel2MaxLength_ = nextLevel2MaxLength_;
  };
  this.getNextLevel2MaxLength_ = function () {
    return this.nextLevel2MaxLength_;
  };
  this.setFinTeam_ = function (finTeam_) {
    this.finTeam_ = finTeam_;
  };
  this.getFinTeam_ = function () {
    return this.finTeam_;
  };
  this.setRotate_ = function (rotate_) {
    this.rotate_ = rotate_;
  };
  this.getRotate_ = function () {
    return this.rotate_;
  };
  this.setChildrenNode_ = function (childrenNode_) {
    this.childrenNode_ = childrenNode_;
  };
  this.getChildrenNode_ = function () {
    return this.childrenNode_;
  };
  this.setLineColor_ = function (lineColor_) {
    this.lineColor_ = lineColor_;
  };
  this.getLineColor_ = function () {
    return this.lineColor_;
  };
  this.setLink_ = function (link_) {
    this.link_ = link_;
  };
  this.getLink_ = function () {
    return this.link_;
  };
  this.setClick_ = function (click_) {
    this.click_ = click_;
  };
  this.getClick_ = function () {
    return this.click_;
  };
  this.toString = function () {
    return (
      "id:[" +
      this.id_ +
      "]   ;fid:[" +
      this.fid_ +
      "]    ;name:[" +
      this.name_ +
      "]    ;level:" +
      this.level_ +
      "   ;upOrDown:" +
      this.upOrDown_ +
      "   ;leaf:" +
      this.leaf_ +
      "   ;NextLevelCount:" +
      this.nextLevelCount_ +
      "   ;nameLength:" +
      this.nameLength_ +
      "   ;finLength_:" +
      this.finLength_ +
      "   ;NextLevelMaxLength_:" +
      this.nextLevelMaxLength_ +
      "   ;NextLevel2MaxLength_:" +
      this.nextLevel2MaxLength_ +
      "   ;finTeam_:" +
      this.finTeam_ +
      "  ; rotate_" +
      this.rotate_ +
      "  ;fromNodePosition_" +
      this.fromNodePosition_ +
      "  ;toNodePosition_" +
      this.toNodePosition_ +
      "  ;childrenNode_" +
      this.childrenNode_ +
      " <br> "
    );
  };
}
