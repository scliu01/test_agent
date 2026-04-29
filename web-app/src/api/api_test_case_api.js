// 导入封装的axios对象
import request from '@/api/request.js';
// 请求模块名称，对应后面的名称
const module_name = 'api_test_case';

class ApiTestCaseApi {
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

	insertBatch(form) {
		return request.post(`/${module_name}/insertBatch`, form);
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

	/**
	 * 导出测试用例
	 * @param {Object} params - 导出参数
	 */
	exportExcel(params) {
		return request.post(`/${module_name}/export_excel`, params, {
			responseType: 'blob', // 设置响应类型为blob，用于处理文件下载
		});
	}

	processWithAIStream(data, options = {}) {
		const { onMessage, onError, onComplete, signal } = options;

		// 手动添加Authorization token
		const headers = {
			'Content-Type': 'application/json',
		};
		const token = localStorage.getItem('access_token');
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}
		return fetch(`/api/${module_name}/process_with_ai_stream`, {
			method: 'POST',
			headers,
			body: JSON.stringify(data),
			signal,
		}).then(async (response) => {
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			let buffer = '';

			try {
				while (true) {
					const { value, done } = await reader.read();
					if (done) {
						// 处理最后可能剩余的数据
						if (buffer.trim()) {
							const lines = buffer.split('\n').filter((line) => line.trim());
							for (const line of lines) {
								try {
									const data = JSON.parse(line);
									onMessage?.(data);
								} catch (e) {
									console.warn('解析最后数据失败:', line, e);
								}
							}
						}
						onComplete?.();
						break;
					}

					// 解码并添加到缓冲区
					const chunk = decoder.decode(value, { stream: true });
					buffer += chunk;

					// 按行分割处理完整的JSON对象
					const lines = buffer.split('\n');

					// 保留最后不完整的行（如果有）
					buffer = lines.pop() || '';

					// 处理完整的行
					for (const line of lines) {
						const trimmedLine = line.trim();
						if (!trimmedLine) continue;

						try {
							const data = JSON.parse(trimmedLine);
							onMessage?.(data);
						} catch (e) {
							console.warn('解析JSON失败:', trimmedLine, e);
							// 如果是JSON解析错误，可能是数据不完整，放回缓冲区
							buffer = trimmedLine + '\n' + buffer;
						}
					}
				}
			} catch (error) {
				onError?.(error);
				throw error;
			}
		});
	}
}

// 导出对象，不导出就无法被其它文件导入使用
export default new ApiTestCaseApi();
