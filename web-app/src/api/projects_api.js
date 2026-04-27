// 导入封装的axios对象
import request from '@/api/request.js';
// 请求模块名称，对应后面的名称
const module_name = 'project';

class ProjectApi {
	// 构造函数
	constructor() {}

	/**
	 * 查询所有数据
	 * @returns 返回所有数据
	 */
	queryAll() {
		// 注意下的是反引号，在ESC键下面那个键
		return request.get(`/${module_name}/queryAll`);
	}

	/**
	 * 密码校验
	 * @param {Object} form 校验的数据
	 * @returns 校验结果
	 */
	openProject(form) {
		return request.post(`/${module_name}/openProject`, form);
	}

	/**
	 * 插入数据
	 * @param {Object} form 插入的数据
	 * @returns 插入结果
	 */
	insert(form) {
		return request.post(`/${module_name}/insert`, form);
	}

	/**
	 * 根据id查询数据
	 * @param {String} id 查询的id
	 * @returns 查询结果
	 */
	queryById(id) {
		return request.get(`/${module_name}/queryById?id=${id}`);
	}

	/**
	 * 更新数据
	 * @param {Object} form 更新的数据
	 * @returns 更新结果
	 */
	update(form) {
		return request.put(`/${module_name}/update`, form);
	}

	/**
	 * 删除数据
	 * @param {String} id 删除的id
	 * @returns 删除结果
	 */
	deleteById(id) {
		return request.delete(`/${module_name}/delete?id=${id}`);
	}
}

// 导出对象，不导出就无法被其它文件导入使用
export default new ProjectApi();
