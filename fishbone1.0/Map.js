function Map_() {
  this.elements = new Array();
  this.size = function () {
    return this.elements.length;
  };
  this.isEmpty = function () {
    return this.elements.length < 1;
  };
  this.clear = function () {
    this.elements = new Array();
  };
  this.put = function (_key, _value) {
    this.remove(_key);
    this.elements.push({ key: _key, value: _value });
  };
  this.remove = function (_key) {
    var bln = false;
    try {
      for (i = 0; i < this.elements.length; i++) {
        if (this.elements[i].key == _key) {
          this.elements.splice(i, 1);
          return true;
        }
      }
    } catch (e) {
      bln = false;
    }
    return bln;
  };
  this.get = function (_key) {
    try {
      for (i = 0; i < this.elements.length; i++) {
        if (this.elements[i].key == _key) {
          return this.elements[i].value;
        }
      }
    } catch (e) {
      return null;
    }
  };
  this.element = function (_index) {
    if (_index < 0 || _index >= this.elements.length) {
      return null;
    }
    return this.elements[_index];
  };
  this.containsKey = function (_key) {
    var bln = false;
    try {
      for (i = 0; i < this.elements.length; i++) {
        if (this.elements[i].key == _key) {
          bln = true;
        }
      }
    } catch (e) {
      bln = false;
    }
    return bln;
  };
  this.containsValue = function (_value) {
    var bln = false;
    try {
      for (i = 0; i < this.elements.length; i++) {
        if (this.elements[i].value == _value) {
          bln = true;
        }
      }
    } catch (e) {
      bln = false;
    }
    return bln;
  };
  this.values = function () {
    var arr = new Array();
    for (i = 0; i < this.elements.length; i++) {
      arr.push(this.elements[i].value);
    }
    return arr;
  };
  this.keys = function () {
    var arr = new Array();
    for (i = 0; i < this.elements.length; i++) {
      arr.push(this.elements[i].key);
    }
    return arr;
  };
}
