function filterCourses()
{
	$('#courses-in-department > tbody > tr').each(function() {
		var courseid = $(this).find('td[id*=id]').html();
		var name = $(this).find('td[id*=name]').html();

		console.log(courseid, name);
		// test
	});
}