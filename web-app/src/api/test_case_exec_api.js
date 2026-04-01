// 导入封装的axios对象
import request from '@/api/request.js';
// 请求模块名称，对应后面的名称
const module_name = 'test_case_exec';

class TestCaseExecApi {
	constructor() { }
	/**
	 * 获取测试用例列表
	 * @param {string} projectId - 项目ID，用于筛选特定项目下的测试用例
	 * @param {string} moduleId - 模块ID，用于筛选特定模块下的测试用例
	 */
	queryAll(projectId, moduleId = '') {
		// 注意下的是反引号，在ESC键下面那个键
		return request.get(`/${module_name}/queryAll?project_id=${projectId}&module_id=${moduleId}`);
	}

	/**
	 * 分页获取测试用例列表
	 * @param {Object} params - 查询参数，包含页码、每页条数等分页信息
	 */
	queryByPage(params) {
		return request.post(`/${module_name}/queryByPage`, params);
	}

	insert(form) {
		return request.post(`/${module_name}/insert`, form);
	}

	/**
	 * 创建 AI 测试任务
	 * @param {Object} form - 包含执行类型和测试用例ID列表的表单数据
	 * @param {string} form.exec_type - 执行类型，例如 'http'
	 * @param {string} form.case_ids - 要执行的测试用例ID列表
	 */
	prepared_task(form) {
		return request.post(`/${module_name}/prepared_task`, form);
	}

	/**
	 * 复制 AI 测试任务
	 * @param {Object} form - 包含执行类型和测试用例ID列表的表单数据
	 * @param {string} form.exec_type - 执行类型，例如 'http'
	 * @param {string} form.case_ids - 要执行的测试用例ID列表
	 */
	copy_task(form) {
		return request.post(`/${module_name}/copy_task`, form);
	}

	update(form) {
		return request.put(`/${module_name}/update`, form);
	}

	queryById(id) {
		// 注意下的是反引号，在ESC键下面那个键
		return request.get(`/${module_name}/queryById?id=${id}`);
	}

	deleteById(id) {
		return request.delete(`/${module_name}/delete?id=${id}`);
	}

	/**
	 * 批量删除测试用例
	 * @param {Array} ids - 要删除的测试用例ID列表
	 */
	deleteBatch(ids) {
		return request.delete(`/${module_name}/deleteBatch`, { data: { ids } });
	}

}

// 导出对象，不导出就无法被其它文件导入使用
export default new TestCaseExecApi();
