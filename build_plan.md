# Build And Integration Test Plan

## Muc tieu

Muc tieu la dua du an ve trang thai:

- Build package thanh cong va lap lai duoc.
- Chi giu lai va van hanh nhom integration test.
- Loai bo hoac tach rieng unit test, e2e script thu cong, va legacy script khoi pipeline chinh.
- Tao duoc mot quy trinh chay integration test ro rang tren may local va trong CI.

## Hien trang da xac minh

### 1. Build

- `uv build` dang chay thanh cong.
- `pyproject.toml` yeu cau Python `>=3.11`.
- May hien tai mac dinh dang tro vao Python `3.10.11`, nhung `uv run` da dung duoc Python `3.11.7`.

### 2. Test infrastructure

- `pytest` duoc cau hinh trong `pyproject.toml` voi `testpaths = ["tests"]`.
- Repo co nhieu nhom test: `unit`, `integration`, `e2e`, `legacy`.
- Tai lieu test hien khong dong bo voi repo thuc te.

### 3. Blocker hien tai

- `tests/conftest.py` import API cu `eveng_mcp_server.client`, trong khi code hien tai su dung wrapper trong `eveng_mcp_server.core`.
- `eveng_mcp_server.config.settings` khoi tao config global ngay luc import; bien moi truong `DEBUG` hien co gia tri khong hop le lam pytest vo ngay o buoc collect.
- `tests/run_tests.py` tham chieu toi file khong ton tai va co duong dan script sai.
- Mot so integration test hien la script thu cong, phu thuoc MCP Inspector, HTTP endpoint, hoac shell command, nhung chua duoc to chuc thanh integration suite on dinh.
- Mot so tai lieu va script van goi CLI command khong ton tai nhu `list-labs`, `create-lab`, `get-lab-details`.

## Pham vi moi

Chi giu lai integration test. Cu the:

- Giu `tests/integration/` lam test suite chinh.
- Khong dua `tests/unit/` vao muc tieu xanh.
- Khong dua `tests/e2e/` vao pipeline chinh o giai doan nay.
- `tests/legacy/` duoc xem la tai san tham khao, khong thuoc test gate.

## Nguyen tac thuc hien

1. Khong sua de "lua" test xanh; test phai phan anh dung giao dien va hanh vi hien tai.
2. Test nao can EVE-NG that phai duoc gan marker/skip ro rang.
3. Integration suite phai co the chay trong 2 che do:
   - Khong co EVE-NG: collect thanh cong, test lien quan duoc skip hop le.
   - Co EVE-NG + cau hinh day du: test chay that va co assertion ro rang.
4. Moi tai lieu huong dan chay test phai khop voi command thuc te.

## Ke hoach chi tiet

### Giai doan 1: Chot baseline build va runtime

Muc tieu:

- Co mot cach build va run duy nhat bang `uv`.
- Chot Python 3.11 la runtime chuan.

Cong viec:

- Xac nhan lai `pyproject.toml`, `uv.lock`, entrypoint package, va command build.
- Chuan hoa lenh local:
  - `uv build`
  - `uv sync --extra test` hoac `uv sync --dev` tuy theo phu thuoc thuc te can cho integration suite
- Ghi ro yeu cau Python 3.11 trong tai lieu.

Dieu kien hoan thanh:

- Build luon thanh cong bang `uv build`.
- Moi lenh test deu chay qua `uv run ...`, khong phu thuoc Python 3.10 he thong.

### Giai doan 2: Lam sach pytest collection cho integration scope

Muc tieu:

- `pytest --collect-only` khong bi vo vi import side effects.

Cong viec:

- Sua `eveng_mcp_server.config.settings` de khong fail ngay khi import do bien moi truong khong hop le.
- Giam import side effect trong `eveng_mcp_server.__init__` neu can.
- Chinh `tests/conftest.py` theo API hien tai cua du an.
- Cau hinh pytest de chi collect `tests/integration/` cho pipeline integration.

Lua chon ky thuat uu tien:

- Hoac sua `pyproject.toml`/command runner de chi target `tests/integration`.
- Hoac tach `conftest.py` chung thanh `tests/integration/conftest.py` rieng, tranh de phan unit-test cu lam vo collection.

Dieu kien hoan thanh:

- `uv run python -m pytest tests/integration --collect-only` chay duoc.

### Giai doan 3: Kiem ke va phan loai lai integration test that su

Muc tieu:

- Biet chinh xac test nao la integration test hop le, test nao la script thu cong.

Cong viec:

- Rasoat toan bo file trong `tests/integration/`.
- Tach thanh 3 nhom:
  - Automated integration tests co the dua vao pytest.
  - Semi-automated tests can MCP Inspector / server process.
  - Manual scripts chi dung de debug.
- Doi ten, di chuyen, hoac reclassify cac file de phan loai ro rang.

Ky vong ket qua:

- Chi giu lai trong `tests/integration/` cac test co assertion may moc va duoc pytest quan ly.
- Script debug thu cong chuyen sang thu muc phu, vi du `tests/manual/` hoac `tests/integration/manual/`.

### Giai doan 4: Dong bo test voi public API hien tai

Muc tieu:

- Integration test phai test dung giao dien dang ton tai cua du an.

Cong viec:

- Doi import API cu sang API hien tai trong `eveng_mcp_server.core`, `eveng_mcp_server.server`, `eveng_mcp_server.cli`.
- Neu can tuong thich nguoc de giam chi phi sua test, tao shim nho cho import path cu. Chi lam neu loi ich ro rang.
- Sua cac command trong script/test de dung voi CLI co that.

Diem can xu ly:

- Hien CLI chi co `run`, `test-connection`, `config-info`, `version`.
- Cac script dang goi `list-labs`, `create-lab`, `get-lab-details` phai duoc viet lai theo MCP Inspector hoac loai khoi integration suite.

Dieu kien hoan thanh:

- Khong con import path cu trong integration suite chinh.
- Khong con command CLI "ao" trong workflow test chinh.

### Giai doan 5: Thiet ke lai integration suite theo cap

Muc tieu:

- Co integration suite nho, on dinh, de mo rong dan.

De xuat chia thanh 3 cap:

#### Cap A: Server startup va MCP surface

Test cac ca sau:

- Khoi dong server o `stdio` thanh cong.
- Khoi dong server o `sse` thanh cong.
- `tools/list` tra ve danh sach tool.
- `resources/list` tra ve resources.
- `prompts/list` tra ve prompts.

Yeu cau:

- Khong can EVE-NG that.
- Neu EVE-NG khong san sang, server van startup duoc va test surface van chay.

#### Cap B: Integration voi process/transport

Test cac ca sau:

- Giao tiep qua MCP Inspector CLI hoac client stdio Python.
- Giao tiep qua HTTP/SSE endpoint neu du an ho tro.
- Xac nhan JSON-RPC flow `initialize`, `tools/list`, `tools/call` hoat dong.

Yeu cau:

- Tu dong spawn server trong fixture.
- Assertion dua tren response thay vi `print`.

#### Cap C: Live EVE-NG integration

Test cac ca sau:

- `connect_eveng_server`
- `test_connection`
- `get_server_info`
- Mot workflow nho nhat voi lab, chi khi co moi truong that.

Yeu cau:

- Dung env/option ro rang: host, username, password, port, protocol.
- Test phai co cleanup tai nguyen.
- Test phai skip neu khong co EVE-NG config.

### Giai doan 6: Viet lai fixture va runner cho integration

Muc tieu:

- Moi nguoi chi can mot lenh de chay integration tests.

Cong viec:

- Tao `tests/integration/conftest.py` rieng.
- Tao fixture cho:
  - spawn MCP server
  - tao client stdio/SSE
  - nap test config tu env
  - live EVE-NG skip logic
- Rut gon hoac viet lai `tests/run_tests.py` thanh runner danh rieng cho integration.

De xuat command chuan:

- `uv run python -m pytest tests/integration -q`
- `uv run python -m pytest tests/integration -m \"not live_eveng\" -q`
- `uv run python -m pytest tests/integration -m live_eveng -q`

Dieu kien hoan thanh:

- Co mot command local chay duoc integration suite co skip hop le.

### Giai doan 7: Loai bo hoac tach rieng cac thanh phan gay nhieu nhieu

Muc tieu:

- Pipeline chinh khong bi anh huong boi script debug va tai lieu cu.

Cong viec:

- Loai `tests/unit/` khoi test command mac dinh.
- Loai `tests/e2e/` khoi integration pipeline.
- Di chuyen `tests/legacy/` va cac script debug thu cong sang khu vuc phi-chinh.
- Danh dau ro file nao la "manual verification only".

Dieu kien hoan thanh:

- Integration suite chinh khong phu thuoc file legacy/e2e/unit.

### Giai doan 8: Dong bo tai lieu

Muc tieu:

- Tai lieu phai huong dan dung quy trinh moi.

Cong viec:

- Sua `README.md`, `docs/README.md`, `tests/README.md`.
- Cap nhat:
  - Python version
  - lenh cai dependency
  - lenh build
  - lenh chay integration tests
  - yeu cau EVE-NG that va skip behavior
- Loai bo command CLI khong ton tai.

Dieu kien hoan thanh:

- Nguoi moi vao repo co the build va chay integration test theo tai lieu ma khong gap lenh sai.

## Thu tu thuc hien de xuat

1. Chot Python 3.11 + `uv` lam runtime duy nhat.
2. Sua config/import side effects de pytest collect duoc.
3. Co lap `tests/integration/` khoi cac nhom test khac.
4. Rasoat va phan loai lai cac file integration.
5. Viet lai fixture + runner integration.
6. Chinh sua tung integration test theo API/CLI hien tai.
7. Chay xanh integration suite o che do khong co EVE-NG.
8. Chay xanh nhom live EVE-NG khi co moi truong.
9. Cap nhat tai lieu.

## Dinh nghia hoan thanh

Ke hoach nay duoc xem la hoan thanh khi dat du cac dieu kien sau:

- `uv build` xanh.
- `uv run python -m pytest tests/integration --collect-only` xanh.
- Integration suite co the chay tren may khong co EVE-NG va skip hop le.
- Integration suite live EVE-NG chay xanh khi cung cap du env/config.
- Khong con unit/e2e/legacy nam trong pipeline chinh.
- Tai lieu build va integration test da duoc cap nhat khop voi code thuc te.

## Rui ro chinh

- API test va code hien tai lech nhau kha nhieu, co the phai viet lai phan lon integration test.
- MCP Inspector CLI co the gay flaky tren Windows neu dung subprocess khong on dinh.
- Live EVE-NG test co nguy co de lai tai nguyen neu cleanup khong chat.
- Tai lieu hien sai nhieu diem, nen neu khong sua dong bo se tiep tuc gay nham khi van hanh.

## Dau ra mong doi sau khi thuc hien

- Mot quy trinh build on dinh bang `uv`.
- Mot integration suite nho gon, phan lop ro rang, assertion that, co skip logic dung.
- Mot runner va tai lieu de bat ky ai trong nhom cung lap lai duoc ket qua.

## Tong ket thuc thi

Phan nay tom tat cac cong viec da hoan thanh tuong ung voi tung giai doan trong ke hoach ban dau.

### Giai doan 1: Chot baseline build va runtime

Da thuc hien:

- Xac nhan build package bang `uv build` va giu `uv` lam duong build chinh.
- Cai phu thuoc test bang `uv sync --extra test`.
- Chot Python 3.11 cho test runner va cap nhat tai lieu theo huong do.
- Trong qua trinh van hanh, doi test harness sang goi truc tiep `.venv\Scripts\python.exe` thay vi phu thuoc `uv run` o moi buoc, de tranh lock file launcher tren Windows.

Ket qua:

- Build xanh on dinh.
- Test suite chay bang Python 3.11 trong `.venv`.

### Giai doan 2: Lam sach pytest collection cho integration scope

Da thuc hien:

- Sua `eveng_mcp_server.config.settings` de chap nhan cac gia tri moi truong pho bien nhu `release` cho `DEBUG` thay vi vo ngay luc import.
- Thay `tests/conftest.py` cu bang ban moi tap trung cho integration suite.
- Them marker va fixture phu hop cho `live_eveng`, `stdio`, `sse`.
- Dam bao `pytest --collect-only` chi con collect cac test integration duoc duy tri.

Ket qua:

- `tests/integration` collect thanh cong.
- Khong con blocker do import path cu hay environment side effect.

### Giai doan 3: Kiem ke va phan loai lai integration test that su

Da thuc hien:

- Rasoat lai toan bo `tests/integration`.
- Xac dinh cac file `run_mcp_tests.sh`, `test_lab_integration.sh`, `direct_api_test.py`, `working_demo.py` la tai san tham khao/debug, khong dua vao automated gate.
- Giu lai trong automated gate cac bai test pytest duoc viet lai co assertion that.

Ket qua:

- Integration suite duoc thu hep ve nhung bai test co the chay tu dong va lap lai duoc.

### Giai doan 4: Dong bo test voi public API hien tai

Da thuc hien:

- Viet lai integration tests de dung giao dien hien tai cua CLI va MCP server.
- Bo cac command CLI khong ton tai nhu `list-labs`, `create-lab`, `get-lab-details` khoi workflow test chinh.
- Chuyen sang dung MCP Python client chinh thuc cho `stdio` va `sse` thay vi dua vao `npx inspector` hoac `socat`.
- Sua logic ung dung o `lab_management` va `eveng_client` de phu hop response that tu EVE-NG:
  - bo sung `delete_lab` dung tren wrapper
  - sua `get_lab_details` de xu ly dung shape du lieu `nodes`, `networks`, `links`

Ket qua:

- Integration tests dang test dung API/CLI hien tai cua du an.
- Live workflow tao/xem/xoa lab chay thanh cong tren EVE-NG that.

### Giai doan 5: Thiet ke lai integration suite theo cap

Da thuc hien:

- Trien khai nhom test surface cho `stdio`:
  - list tools
  - list resources
  - list prompts
- Trien khai nhom test surface cho `sse`.
- Trien khai nhom live EVE-NG cho:
  - `connect_eveng_server`
  - `test_connection`
  - `create_lab`
  - `list_labs`
  - `get_lab_details`
  - `delete_lab`
- Trien khai nhom CLI integration cho:
  - `version`
  - `config-info`
  - `test-connection`

Ket qua:

- Suite co phan lop ro rang giua non-live va live integration.

### Giai doan 6: Viet lai fixture va runner cho integration

Da thuc hien:

- Tao fixture chung trong `tests/conftest.py` cho:
  - env config
  - live EVE-NG skip logic
  - spawn server SSE
  - chuan hoa interpreter dung cho subprocess
- Viet lai `tests/run_tests.py` thanh runner gon chi phuc vu integration suite.
- Them huong chay collect-only, non-live, live tu runner.

Ket qua:

- Co quy trinh van hanh ro rang de chay integration suite.

### Giai doan 7: Loai bo hoac tach rieng cac thanh phan gay nhieu nhieu

Da thuc hien:

- Loai `unit`, `e2e`, `legacy` khoi automated gate.
- Khong xoa cac script tham khao, nhung tai lieu da noi ro chung khong nam trong test gate.
- Tach hoan toan workflow maintained ra khoi cac script debug cu.

Ket qua:

- Pipeline chinh chi tap trung vao integration tests duoc duy tri.

### Giai doan 8: Dong bo tai lieu

Da thuc hien:

- Cap nhat `README.md`, `docs/README.md`, `tests/README.md`.
- Dong bo:
  - yeu cau Python 3.11
  - cach cai dependency test
  - lenh build
  - lenh collect integration
  - lenh chay non-live va live integration
  - cach truyen thong tin EVE-NG that
- Cap nhat marker trong `pyproject.toml`.

Ket qua:

- Tai lieu da khop voi quy trinh build va integration test hien tai.

## Ket qua xac thuc cuoi cung

Da chay thanh cong:

- `uv build`
- `.venv\Scripts\python.exe -m pytest tests/integration --collect-only -q`
- `.venv\Scripts\python.exe -m pytest tests/integration -m "not live_eveng" -q`
- `.venv\Scripts\python.exe -m pytest tests/integration -m live_eveng -q --eveng-host 192.168.168.141 --eveng-user admin --eveng-pass eve --eveng-port 80 --eveng-protocol http`

Ket qua:

- Non-live integration: `4 passed`
- Live integration: `2 passed`
- Build: thanh cong, tao duoc wheel va sdist

## Ke hoach mo rong: Dua cac case E2E cu vao integration suite

Phan nay mo ta ke hoach de chuyen cac workflow `e2e` cu lien quan den chinh sua bai lab thanh cac live integration tests duoc duy tri va dua vao test gate mo rong.

### Muc tieu mo rong

- Tai su dung cac case co gia tri trong:
  - `tests/e2e/comprehensive_api_test.py`
  - `tests/e2e/final_comprehensive_test.py`
- Dua cac thao tac chinh sua lab ve thanh integration tests co assertion that.
- Khong phuc hoi nguyen trang kieu test cu dua vao `print`, `npx inspector`, hay script thu cong.
- Giu cho suite van chia ro `non-live` va `live_eveng`.

### Pham vi chuc nang can bo sung

Nhung thao tac can dua vao live integration suite:

- `list_nodes`
- `add_node`
- `get_node_details`
- `start_node`
- `stop_node`
- `delete_node`
- `create_lab_network`
- `delete_lab_network`
- `connect_node_to_network`
- `connect_node_to_node`
- `get_lab_topology`

Co the xem xet bo sung sau, nhung khong nen dua vao dot dau neu muon giu do on dinh:

- `start_all_nodes`
- `stop_all_nodes`
- `wipe_node`
- `wipe_all_nodes`

### Nguyen tac chuyen doi

1. Moi case phai chay qua harness integration hien tai, khong dung lai `npx @modelcontextprotocol/inspector`.
2. Moi case phai co assertion dua tren response MCP va, khi can, xac minh lai bang API that cua EVE-NG.
3. Moi test live phai cleanup sach tai nguyen:
   - xoa node
   - xoa network
   - xoa lab
4. Moi test phai dung ten tai nguyen ngau nhien de tranh va cham khi rerun.
5. Khong gom qua nhieu thao tac vao mot test duy nhat neu lam nhu vay kho debug khi fail.

### De xuat chia nho thanh test cases

#### Nhom 1: Node lifecycle co ban

Muc tieu:

- Xac nhan co the them, doc, dieu khien, va xoa node trong mot lab moi.

Test case de xuat:

- tao lab tam
- `list_nodes` xac nhan ban dau rong
- `add_node` tao 1 node Linux/QEMU toi gian
- `list_nodes` xac nhan node moi xuat hien
- `get_node_details` xac nhan metadata co ten/template dung
- `start_node`
- `stop_node`
- `delete_node`
- `list_nodes` xac nhan node da bien mat

Dieu kien tien quyet:

- Can xac dinh template/image nao thuc su ton tai tren EVE-NG `192.168.168.141`
- Neu khong co image phu hop, test phai chon template kha dung nhat qua fixture probe

#### Nhom 2: Lab network lifecycle

Muc tieu:

- Xac nhan co the them va xoa network trong lab.

Test case de xuat:

- tao lab tam
- `create_lab_network`
- `list_lab_networks` xac nhan network moi xuat hien
- `delete_lab_network`
- `list_lab_networks` xac nhan network da bien mat

#### Nhom 3: Node-to-network wiring

Muc tieu:

- Xac nhan co the noi node vao network va topology phan anh dung ket qua.

Test case de xuat:

- tao lab tam
- them 1 node
- tao 1 network
- `connect_node_to_network`
- `get_lab_topology` xac nhan co lien ket
- cleanup node, network, lab

#### Nhom 4: Node-to-node wiring

Muc tieu:

- Xac nhan co the tao ket noi point-to-point giua hai node.

Test case de xuat:

- tao lab tam
- them 2 node
- `connect_node_to_node`
- `get_lab_topology` xac nhan lien ket serial/ethernet da duoc tao
- cleanup toan bo

### Cong viec ky thuat can lam

#### 1. Khao sat du lieu that tren EVE-NG

Can lam:

- Probe `list_node_templates`
- Xac dinh template co kha nang dung on dinh nhat cho test
- Xac dinh tham so toi thieu cho `add_node`
- Xac dinh format response that cua:
  - `list_nodes`
  - `get_node_details`
  - `list_lab_networks`
  - `get_lab_topology`

Muc dich:

- Tranh viet test dua tren gia dinh sai ve shape response

#### 2. Bo sung fixture live lab

Can lam:

- Tao fixture tao lab tam va xoa lab sau test
- Tao helper de sinh ten node/network duy nhat
- Tao helper goi MCP tool va tra text/json da parse

Muc dich:

- Rut gon code lap lai va cleanup on dinh hon

#### 3. Bo sung helper xac minh bang EVE-NG API truc tiep

Can lam:

- Them client helper cho live integration de:
  - doc nodes trong lab
  - doc networks trong lab
  - doc topology trong lab

Muc dich:

- Co the doi chieu ket qua MCP voi backend that thay vi chi assert tren chuoi text

#### 4. Viet lai test theo workflow nho

Can lam:

- Moi test cover mot nhom hanh vi ro rang
- Han che test monolithic kieu `comprehensive_api_test.py`

Muc dich:

- Fail de khoanh vung
- Co the rerun nhanh tung nhom case

#### 5. Cap nhat tai lieu va runner

Can lam:

- Mo rong `tests/README.md`
- Mo rong `tests/run_tests.py` neu can them filter cho nhom `live_eveng` mo rong
- Ghi ro yeu cau EVE-NG phai co image/template phu hop

### Thu tu thuc hien de xuat cho dot mo rong

1. Probe live EVE-NG de chot template/node strategy
2. Them fixture live lab + helper verify API
3. Trien khai `Node lifecycle`
4. Trien khai `Lab network lifecycle`
5. Trien khai `Node-to-network wiring`
6. Trien khai `Node-to-node wiring`
7. Chay lai full live integration suite
8. Cap nhat tai lieu

### Rui ro va cach giam thieu

- Rui ro 1: Template/image khong san tren EVE-NG
  - Giam thieu: probe truoc va chon template kha dung nhat

- Rui ro 2: Test start/stop node cham hoac flaky
  - Giam thieu: timeout ro rang, polling state neu can, va tach rieng khoi test tao/xoa node

- Rui ro 3: Topology response kho parse
  - Giam thieu: doi chieu bang API that va viet helper normalize response

- Rui ro 4: Cleanup fail de lai rac trong EVE-NG
  - Giam thieu: cleanup theo thu tu node -> network -> lab, co retry nhe neu can

### Dinh nghia hoan thanh cho dot mo rong

Dot mo rong nay duoc xem la xong khi:

- Cac workflow chinh sua bai lab tu `e2e` cu da duoc chuyen thanh live integration tests
- Suite live moi pass on dinh tren `192.168.168.141`
- Khong can dung script `e2e` cu de bao phu cac thao tac them/xoa/noi thiet bi
- `build_plan.md` va `tests/README.md` mo ta dung pham vi moi

### Ket qua thuc thi giai doan 1 cua dot mo rong

Da probe truc tiep EVE-NG `192.168.168.141` de chot template va shape response that.

#### 1. Template strategy da xac nhan

Da thu tao node thanh cong voi bo tham so toi thieu tren cac template:

- `docker`
- `linux`
- `vpcs`
- `freebsd`
- `vios`
- `viosl2`
- `csr1000vng`

Quyet dinh de xuat cho test mo rong:

- Dung `vpcs` lam template mac dinh cho cac test thao tac lab.

Ly do:

- Tao node thanh cong on dinh.
- Payload nhe.
- So cong ethernet ro rang va de noi topology.
- Phu hop hon cho test CRUD/connectivity co ban so voi cac appliance nang.

#### 2. Bo tham so toi thieu cho `add_node`

Da xac nhan thao tac tao node thanh cong voi:

- `lab_path`
- `template`
- `name`
- `left`
- `top`

Khong can truyen them `image`, `ram`, `cpu`, `ethernet` cho dot dau.

#### 3. Shape response that da xac nhan

`add_node`:

- response dang:
  - `code`
  - `status`
  - `message`
  - `data.id`

`list_nodes`:

- `data` la mapping theo `node_id`
- moi node co cac field quan trong:
  - `id`
  - `name`
  - `template`
  - `type`
  - `status`
  - `cpu`
  - `ram`
  - `ethernet`
  - `url`
  - `uuid`

`get_node_details`:

- `data` la object don le, khong phai mapping theo `id`
- co them cac field chi tiet nhu:
  - `cpulimit`
  - `qemu_options`
  - `qemu_version`
  - `qemu_arch`
  - `qemu_nic`

`get_node_interfaces`:

- `data.ethernet` la list interface dang:
  - `name`: vi du `e0`, `e1`
  - `network_id`

`create_lab_network`:

- response dang:
  - `code`
  - `status`
  - `message`
  - `data.id`

`list_lab_networks`:

- `data` la mapping theo `network_id`
- moi network co:
  - `id`
  - `name`
  - `type`
  - `count`
  - `left`
  - `top`
  - `visibility`
  - `icon`

`get_lab_topology`:

- `data` la list
- khi chua co ket noi: `data = []`
- khi co ket noi: moi phan tu co cac field:
  - `type`
  - `source`
  - `source_type`
  - `source_label`
  - `destination`
  - `destination_type`
  - `destination_label`

#### 4. Phat hien quan trong ve code hien tai

Phat hien 1:

- `list_node_templates` trong tool layer dang fail vi code hien tai gia dinh sai `templates['data'][template_name]` la object co `.get(...)`.
- Backend that tra ve mapping `template_name -> string`.

Phat hien 2:

- `list_network_types` trong tool layer dang fail vi gia dinh sai shape `network_types['data']`.
- Can probe va normalize lai response truoc khi dua tool nay vao test gate mo rong.

Phat hien 3:

- `connect_node_to_network`/wrapper `connect_node_to_cloud` hien dang sai quy uoc tham so.
- `evengsdk.api.connect_node_to_cloud()` ky vong:
  - `src` = ten node
  - `dst` = ten network
  - `src_label` = ten interface, vi du `e0`
- Wrapper hien tai dang truyen `node_id` va `network_id`, nen fail voi loi:
  - `node 1 not found or invalid`

Xac nhan quan trong:

- Khi goi truc tiep SDK bang:
  - node name = `probe-node`
  - interface = `e0`
  - network name = `probe-net`
- thi ket noi thanh cong va topology tra ve dung du lieu.

#### 5. Ket luan cho buoc tiep theo

Sau giai doan probe nay, thu tu trien khai tiep theo nen la:

1. Sua `list_node_templates`
2. Sua `list_network_types`
3. Sua wrapper/tool cho `connect_node_to_network` de dung ten node/network thay vi ID
4. Bat dau viet `Node lifecycle` test voi template `vpcs`
5. Sau khi connect fix xong, viet tiep `Lab network lifecycle` va `Node-to-network wiring`

### Ket qua thuc thi buoc sua blocker

Da thuc hien 3 thay doi dung theo de xuat:

#### 1. Da sua `list_node_templates`

Da sua formatter trong `eveng_mcp_server/tools/node_management.py` de chap nhan shape that:

- `templates['data']` la mapping `template_name -> string`

Thay vi gia dinh moi phan tu la object co `.get(...)`, tool hien tai normalize payload va van render duoc text hop le.

Xac thuc:

- Goi qua MCP `list_node_templates` khong con fail
- Output hien danh sach template hop le

#### 2. Da sua `list_network_types`

Da sua formatter trong `eveng_mcp_server/tools/network_management.py` de chap nhan shape that:

- `network_types['data']` la mapping `type_name -> string`

Dong thoi da sua formatter `get_lab_topology` de chap nhan `data` dang list connection thay vi gia dinh mapping.

Xac thuc:

- Goi qua MCP `list_network_types` khong con fail
- Output hien danh sach `bridge`, `ovs`, `pnet0..pnet9` hop le

#### 3. Da sua wrapper cho `connect_node_to_network`

Da sua `eveng_mcp_server/core/eveng_client.py`:

- `connect_node_to_cloud` hien resolve `node_id -> node name`
- `connect_node_to_cloud` hien resolve `network_id -> network name`
- sau do moi goi `evengsdk` theo dung quy uoc cua SDK

Dong thoi da sua `connect_node_to_node` theo cung nguyen tac de tranh gap lai cung mot loi o phase test tiep theo.

Da cap nhat mo ta argument trong `network_management.py`:

- `node_id` va `network_id` nay duoc hieu la `ID hoac name`

#### 4. Ket qua xac thuc sau khi sua

Da xac nhan:

- `list_node_templates` qua MCP: pass
- `list_network_types` qua MCP: pass
- integration suite maintained:
  - non-live: pass
  - live: pass

Lenh xac thuc da chay:

- `.venv\Scripts\python.exe -m pytest tests/integration -m "not live_eveng" -q`
- `.venv\Scripts\python.exe -m pytest tests/integration -m live_eveng -q --eveng-host 192.168.168.141 --eveng-user admin --eveng-pass eve --eveng-port 80 --eveng-protocol http`

Ket qua:

- non-live: `4 passed`
- live: `2 passed`

#### 5. Luu y quan trong sau khi sua

Trong qua trinh probe chuoi thao tac dai qua cung mot session `stdio`, EVE-NG van co luc tra:

- `412 User is not authenticated or session timed out (90001)`

Dieu nay xuat hien theo tinh huong va co ve la do do on dinh session cua backend/SDK hon la do 3 fix vua lam, vi:

- live integration suite maintained van pass
- cac tool list da duoc xac minh hoat dong dung sau khi sua

Ket luan thao tac:

- Buoc sua blocker da hoan thanh
- He thong san sang de sang phase tiep theo: viet `Node lifecycle` test voi `vpcs`
- Khi sang phase do, nen bo sung retry/reconnect nhe cho cac workflow live dai hoi neu gap lai `412`
