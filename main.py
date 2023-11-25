import tkinter as tk
from tkinter import messagebox


class UI:
    def __init__(self, controller):
        self.controller = controller

        self.root = tk.Tk()
        self.root.title("Optimization Tool")

        # 输入框
        self.objfunc_label = tk.Label(self.root, text="Objective Function:")
        self.objfunc_var = tk.StringVar(value=[0, 0, 0, 0, 0])  # 初始值为【0，0，0，0，0】
        self.objfunc_entry = tk.Entry(self.root, textvariable=self.objfunc_var)

        self.const_label = tk.Label(self.root, text="Constraint: Please <RETURN> after each Constraint!!")
        self.const_entries = [
            tk.Entry(self.root, textvariable=tk.StringVar(value=[0, 0, 0, 0, 0, 0]))]  # 初始值为[0, 0, 0, 0, 0, 0])]

        # 按钮
        self.add_const_button = tk.Button(self.root, text="Add Constraint", command=self.add_const_entry)
        self.remove_const_button = tk.Button(self.root, text="Remove Constraint", command=self.remove_const_entry)
        self.calculate_button = tk.Button(self.root, text="Calculate", command=self.click_cal_but)

        # 放置控件
        self.objfunc_label.pack()
        self.objfunc_entry.pack()
        self.objfunc_entry.bind("<Return>", lambda event: self.type_objfunc())
        self.const_label.pack()
        for entry in self.const_entries:
            entry.bind("<Return>", lambda event: self.type_constraint())
            entry.pack()
        self.add_const_button.pack(side=tk.BOTTOM)
        self.remove_const_button.pack(side=tk.BOTTOM)
        self.calculate_button.pack(side=tk.BOTTOM)

    def type_constraint(self):
        # 获取约束条件
        all_constraints = [[float(entry) for entry in const_entry.get().split()] for const_entry in self.const_entries]
        # 将所有约束条件传递给Controller
        self.controller.create_constraint(all_constraints)

    def type_objfunc(self):
        # 获取目标函数
        objfunc_input = [float(entry) for entry in self.objfunc_entry.get().split()]
        self.controller.create_objfunc(objfunc_input)

    def click_cal_but(self):
        # 用户点击计算按钮
        result = self.controller.calculate()
        result_window = tk.Toplevel(self.root)
        result_window.title("Result")

        result_label = tk.Label(result_window, text=f"输出结果为: {result.zmax}\n对应取值为:{result.cons_vari}")
        result_label.pack()

        save_button = tk.Button(result_window, text="Save Result", command=self.click_sav_but)
        save_button.pack()

    def click_sav_but(self):
        # 用户点击保存按钮
        self.controller.save()

    def add_const_entry(self):
        # 增加约束条件输入框
        const_entry = tk.Entry(self.root, textvariable=tk.StringVar(value=[0, 0, 0, 0, 0, 0]))
        const_entry.bind("<Return>", lambda event: self.type_constraint())
        self.const_entries.append(const_entry)
        const_entry.pack()

    def remove_const_entry(self):
        # 移除最后一个约束条件输入框
        if self.const_entries:
            const_entry = self.const_entries.pop()
            const_entry.destroy()


class JiefangSystem:
    def run(self, ui):
        # Jiefang System 运行逻辑
        ui.root.mainloop()


class Model:
    def __init__(self, obj_func, const_func_list, cal):
        self.of = obj_func
        self.cfl = const_func_list
        self.standard_array = []
        self.calculator = cal
        self.method = Method()

    def cal_model(self):
        # 先转换出standard_array
        conv = Converter()
        self.standard_array = conv.convert(self.of, self.cfl)
        print("转化后的标准方程组为：", self.standard_array)

        # 利用standard_array计算
        self.method = self.calculator.sel_version(self.of, self.standard_array)


class Controller:
    def __init__(self, const_func_list, obj_func):
        self.const_func_list = const_func_list
        self.obj_func = obj_func
        self.model = Model(obj_func, const_func_list, Calculator())

    def create_objfunc(self, objfunc_input):
        self.obj_func.create(objfunc_input)

    def create_constraint(self, const_input):
        self.const_func_list.add(const_input)

    def calculate(self):
        self.model = Model(self.obj_func, self.const_func_list, Calculator())
        self.model.cal_model()
        # 在计算完成后，调用UI的方法显示结果窗口
        return self.model.method

    def save(self):
        # 在这里调用模型的保存结果逻辑
        save = Save(self.model.method)
        save.save_result()


class Save:
    def __init__(self, m):
        self.suc = True
        self.fail = False
        self.method = m

    def save_result(self):
        # 保存计算结果逻辑
        result_str = f"Result is: {self.method.zmax}, {self.method.cons_vari}"
        print(result_str)
        with open('result.txt', 'w') as file:
            file.write(result_str)
        messagebox.showinfo("Result", f"Result saved: {self.method.zmax}, {self.method.cons_vari}")



class ConstFuncList:
    def __init__(self):
        self.constraints_array = []
        self.cons_num = len(self.constraints_array)

    def add(self, const_input):
        self.constraints_array = const_input
        self.cons_num = len(self.constraints_array)
        print("You have", self.cons_num, "Constraints which are:", self.constraints_array)


# 用不上！
# class ConstFunc:
#     def __init__(self):
#         self.array = [0, 0, 0, 0, 0, 0]  # 初始值为[0, 0, 0, 0, 0]


class ObjectFunction:
    def __init__(self):
        self.array = [0, 0, 0, 0, 0]  # 初始值为[0, 0, 0, 0, 0]
        self.obj_num = sum(1 for element in self.array if element != 0)

    def create(self, objfunc_input):
        # 创建目标函数逻辑
        self.array = objfunc_input
        self.obj_num = sum(1 for element in self.array if element != 0)
        print("Your Object Function is:", self.array)


class Method:
    def __init__(self):
        self.cons_vari = []
        self.zmax = 0.0


class Calculator:
    def __init__(self):
        self.standard_array = []
        self.ver = Calculator_v1()
        self.method = Method()

    def sel_version(self, objfunc, standard_a):
        self.standard_array = standard_a
        self.method.cons_vari, self.method.zmax = self.ver.calc(objfunc)
        print('计算结果为：', self.method.zmax, '对应取值为：', self.method.cons_vari)
        return self.method


class Calculator_v1:
    def __init__(self):
        self.version = 1
        self.result_array = []

    def calc(self, objfunc):
        self.result_array = [1.0] * objfunc.obj_num
        result = 0
        for iter in range(objfunc.obj_num):
            result = result + self.result_array[iter] * objfunc.array[iter]

        return self.result_array, result


class Calculator_v2:
    def __init__(self):
        self.version = 2
        self.result_array = []

    def calc(self, objfunc):
        self.result_array = [1.0] * objfunc.obj_num
        result = 0
        for iter in range(objfunc.obj_num):
            result = result + self.result_array[iter] * objfunc.array[iter]

        print('计算结果为：', result, '对应取值为：', self.result_array)
        return self.result_array, result


class Converter:
    def __init__(self):
        self.standard_array = []

    def convert(self, obj, cfl):
        obj_a = obj.array
        cfl_a = cfl.constraints_array
        obj_num = obj.obj_num
        cfl_num = cfl.cons_num

        # 1、先将objfunction转换
        obj_a = [element for element in obj_a if element != 0]
        obj_a = obj_a + [0.0] * cfl_num
        # 将数组中的所有值取反
        added_array = [-value for value in obj_a]
        # 在数组最前面和最后面各加一位
        processed_array = [1.0] + added_array + [0.0]

        self.standard_array.append(processed_array)

        # 2、再将constraintfunction转换
        flag = 1
        for constraint in cfl_a:
            tmp_a = constraint[:obj_num]
            res = [0.0] + tmp_a + [0.0] * cfl_num + [constraint[-1]]
            res[obj_num + flag] = 1.0
            flag += 1

            self.standard_array.append(res)

        return self.standard_array


if __name__ == "__main__":
    jf = JiefangSystem()
    const_func_list = ConstFuncList()
    obj_func = ObjectFunction()
    controller = Controller(const_func_list, obj_func)

    ui = UI(controller)

    # 解放system启动
    jf.run(ui)
