import time
import threading


def do_something(num):
    lock.acquire()
    print('线程 %d 启动' % num)
    result.append(num)
    lock.release()

    time.sleep(1)
    print('线程 %d 结束' % num)
    return 1




start = time.perf_counter()
lock = threading.Lock()
thread_list = []
result = []

max_connections = 10
pool_sema = threading.BoundedSemaphore(max_connections)

for i in range(1, 20):
    pool_sema.acquire()
    thread = threading.Thread(target=do_something, args=[i])
    thread.start()
    pool_sema.release()

finish = time.perf_counter()
print(f"全部任务执行完成，耗时 {round(finish - start,2)} 秒")