// 正则表达式定义
/**
 * - username 4~30 位,字母、汉字、数字、连字符（-），不能以数字开头，不能包含空格
 *  password 8~12 位 字母、数字、特殊字符（!@#$%^&*()_+）,至少包含字母和数字，不能包含空格和汉字
-* email 最长50个字符，也可以没有
 */
 const usernameRegex = /^[a-zA-Z\u4e00-\u9fa5][a-zA-Z0-9\u4e00-\u9fa5-]{3,29}$/;
const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[!-~]{8,12}$/;
const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/

export default {
  usernameRegex,
  passwordRegex,
  emailRegex
};
